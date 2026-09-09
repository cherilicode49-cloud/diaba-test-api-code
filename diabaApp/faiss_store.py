import faiss
import numpy as np
from threading import Lock
from . import models
import torch
import torchvision.models as torchmodels
import torchvision.transforms as transforms
import clip
import os
import time

import threading

FAISS_INDEX = None
PRODUCT_IDS = None
FAISS_LOCK = Lock()

FAISS_REBUILDING = False

CACHE_CATEGORIES = []
TEXT_FEATURES = None

device = "cuda" if torch.cuda.is_available() else "cpu"
clip_model, preprocess = clip.load("ViT-B/32", device=device)

# model = torchmodels.efficientnet_b0(weights=torchmodels.EfficientNet_B0_Weights.DEFAULT)
# model.eval()
# model = model.to(device)
feature_extractor = torch.nn.Sequential(*list(clip_model.children())[:-1]).to(device)

def build_faiss_index():

    print(
    "BUILD PROCESS:",
    os.getpid()
)

    global FAISS_INDEX
    global PRODUCT_IDS

    print("Building FAISS index...")

    vector_fields = [
        "product_image_1_vector",
        "product_image_2_vector",
        "product_image_3_vector",
        "product_image_4_vector",
        "product_image_5_vector",
        "product_image_6_vector",
        "product_image_7_vector",
        "product_image_8_vector",
    ]

    products = models.ProductDetail.objects.only(
        "id",
        *vector_fields
    )
    print(
    "BUILD PROCESS:",
    os.getpid()
)

    vectors = []
    ids = []

    for p in products.iterator(chunk_size=1000):

        for field in vector_fields:

            vector_data = getattr(p, field)

            # print("field======>",field)
            # print("field======>",vector_data)

            if not vector_data:
                continue

            try:
                vec = np.array(
                    vector_data,
                    dtype=np.float32
                ).flatten()

                if vec.shape[0] != 512:
                    continue

                faiss.normalize_L2(
                    vec.reshape(1, -1)
                )

                vectors.append(vec)

                ids.append(p.id)
            except Exception as e:
                # print("error--->",e)
                continue

    print(
    "BUILD PROCESS:",
    os.getpid()
)
    
    if not vectors:
        print("No vectors found")
        return

    vectors_np = np.array(
        vectors,
        dtype=np.float32
    )

    ids_np = np.array(ids)

    new_index = faiss.IndexFlatIP(512)

    new_index.add(vectors_np)

    with FAISS_LOCK:

        global FAISS_INDEX
        global PRODUCT_IDS

        FAISS_INDEX = new_index
        PRODUCT_IDS = ids_np

# def get_faiss_index():
#     global FAISS_INDEX

#     if FAISS_INDEX is None:
#         with FAISS_LOCK:

#             if FAISS_INDEX is None:
#                 build_faiss_index()
        
#     print(f"FAISS_INDEX ----> {FAISS_INDEX} ,PRODUCT_IDS -----> {PRODUCT_IDS}",FAISS_INDEX,PRODUCT_IDS)

#     return FAISS_INDEX, PRODUCT_IDS

def get_faiss_index():
    print(
        "SEARCH PROCESS:",
        os.getpid()
    )

    global FAISS_INDEX
    global PRODUCT_IDS

    if FAISS_INDEX is None:
        build_faiss_index()

    with FAISS_LOCK:

        return (
            FAISS_INDEX,
            PRODUCT_IDS
        )
    
    print(
    "SEARCH PROCESS:",
    os.getpid()
)


def refresh_faiss_index():
    with FAISS_LOCK:
        build_faiss_index()


def async_refresh_faiss():

    global FAISS_REBUILDING

    if FAISS_REBUILDING:
        return

    def rebuild():

        global FAISS_REBUILDING

        try:

            FAISS_REBUILDING = True

            print(
                "Starting FAISS rebuild..."
            )
            time.sleep(30)

            build_faiss_index()

            print(
                "FAISS rebuild completed"
            )

        except Exception as e:

            print(
                "FAISS rebuild error =====>",
                e
            )

        finally:

            FAISS_REBUILDING = False

    threading.Thread(
        target=rebuild,
        daemon=True
    ).start()


def preload_clip_categories():

    global CACHE_CATEGORIES
    global TEXT_FEATURES

    print("Loading CLIP category embeddings...")

    CACHE_CATEGORIES = list(
        models.ProductDetail.objects
        .values_list(
            "subcategory__subcategory",
            flat=True
        )
        .distinct()
    )

    CACHE_CATEGORIES = [
        c for c in CACHE_CATEGORIES
        if c
    ]

    if not CACHE_CATEGORIES:
        print("No categories found")
        return

    with torch.no_grad():

        text_tokens = clip.tokenize(
            CACHE_CATEGORIES
        ).to(device)

        TEXT_FEATURES = clip_model.encode_text(
            text_tokens
        )

        TEXT_FEATURES /= TEXT_FEATURES.norm(
            dim=-1,
            keepdim=True
        )

    return CACHE_CATEGORIES, TEXT_FEATURES