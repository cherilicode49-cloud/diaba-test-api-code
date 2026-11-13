from django.core.management.base import BaseCommand
from django.db import transaction
from diabaApp import models
from decimal import Decimal


class Command(BaseCommand):
    help = "Converts product and variant base prices between XOF and USD."

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview changes without modifying the database.'
        )
        parser.add_argument(
            '--reverse',
            action='store_true',
            help='Revert prices from USD back to XOF.'
        )
        parser.add_argument(
            '--rate',
            type=float,
            default=None,
            help='Custom XOF rate to use. Defaults to CurrencyConverter system_rate for XOF.'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        reverse = options['reverse']
        custom_rate = options['rate']

        xof_obj = models.CurrencyConverter.objects.filter(currency_code="XOF").first()
        if not xof_obj or not xof_obj.system_rate:
            self.stderr.write(self.style.ERROR("CurrencyConverter for XOF not found or has no system_rate."))
            return

        rate = custom_rate if custom_rate else float(xof_obj.system_rate)
        if rate <= 0:
            self.stderr.write(self.style.ERROR(f"Invalid XOF rate: {rate}"))
            return

        direction = "USD -> XOF (REVERT)" if reverse else "XOF -> USD"
        self.stdout.write(self.style.NOTICE(f"=== Starting Base Price Conversion ==="))
        self.stdout.write(f"Direction: {direction}")
        self.stdout.write(f"XOF Rate: {rate}")
        self.stdout.write(f"Dry Run: {dry_run}\n")

        # 1. ProductDetail
        products = list(models.ProductDetail.objects.all().only('id', 'product_name', 'price'))
        self.stdout.write(f"Found {len(products)} ProductDetail records.")

        # Show samples
        samples_p = products[:3]
        self.stdout.write("Sample ProductDetail conversions:")
        for p in samples_p:
            old_p = float(p.price) if p.price is not None else 0.0
            new_p = round(old_p * rate, 2) if reverse else round(old_p / rate, 2)
            self.stdout.write(f"  [ID {p.id}] {p.product_name[:30]}... : {old_p} -> {new_p}")

        # 2. ProductModelVariant
        variants = list(models.ProductModelVariant.objects.all().only('id', 'name', 'price'))
        self.stdout.write(f"\nFound {len(variants)} ProductModelVariant records.")
        samples_v = variants[:3]
        self.stdout.write("Sample ProductModelVariant conversions:")
        for v in samples_v:
            try:
                old_v = float(v.price) if v.price not in [None, '', 'null'] else 0.0
            except (ValueError, TypeError):
                old_v = 0.0
            new_v = round(old_v * rate, 2) if reverse else round(old_v / rate, 2)
            self.stdout.write(f"  [ID {v.id}] {v.name} : {old_v} -> {new_v}")

        # 3. VendorProductPrice
        vendor_prices = list(models.VendorProductPrice.objects.all().only('id', 'price'))
        self.stdout.write(f"\nFound {len(vendor_prices)} VendorProductPrice records.")

        if dry_run:
            self.stdout.write(self.style.WARNING("\n[DRY RUN] No changes were written to the database."))
            return

        # Execute updates in a transaction
        with transaction.atomic():
            # Update ProductDetail
            p_to_update = []
            for p in products:
                if p.price is not None:
                    try:
                        old_val = float(p.price)
                        p.price = round(old_val * rate, 2) if reverse else round(old_val / rate, 2)
                        p_to_update.append(p)
                    except (ValueError, TypeError):
                        pass

            models.ProductDetail.objects.bulk_update(p_to_update, ['price'], batch_size=500)
            self.stdout.write(self.style.SUCCESS(f"Updated {len(p_to_update)} ProductDetail records."))

            # Update ProductModelVariant
            v_to_update = []
            for v in variants:
                if v.price not in [None, '', 'null']:
                    try:
                        old_val = float(v.price)
                        new_val = round(old_val * rate, 2) if reverse else round(old_val / rate, 2)
                        v.price = str(new_val)
                        v_to_update.append(v)
                    except (ValueError, TypeError):
                        pass

            models.ProductModelVariant.objects.bulk_update(v_to_update, ['price'], batch_size=500)
            self.stdout.write(self.style.SUCCESS(f"Updated {len(v_to_update)} ProductModelVariant records."))

            # Update VendorProductPrice
            vp_to_update = []
            for vp in vendor_prices:
                if vp.price not in [None, '', 'null']:
                    try:
                        old_val = float(vp.price)
                        new_val = round(old_val * rate, 2) if reverse else round(old_val / rate, 2)
                        vp.price = str(new_val)
                        vp_to_update.append(vp)
                    except (ValueError, TypeError):
                        pass

            models.VendorProductPrice.objects.bulk_update(vp_to_update, ['price'], batch_size=500)
            self.stdout.write(self.style.SUCCESS(f"Updated {len(vp_to_update)} VendorProductPrice records."))

        self.stdout.write(self.style.SUCCESS(f"\nSuccessfully completed {direction} conversion!"))

