from django.db import models
from diabaApp import validators
from datetime import datetime
from .customer_models import CustomerDetail, CustomerAddressDetail

from .admin_models import AdminDetail, ChatAgentDetail


class ChatRoom(models.Model):
    user = models.ForeignKey(CustomerDetail,verbose_name = 'User', null=True, blank = True, on_delete=models.CASCADE)
    admin = models.ForeignKey(AdminDetail, verbose_name = 'Admin', null=True, blank = True, on_delete=models.SET_NULL)
    chat_agent = models.ForeignKey(ChatAgentDetail, verbose_name = 'Chat Agent', null=True, blank = True, on_delete=models.CASCADE)
    room = models.CharField(verbose_name='Room ID', null=True, blank=True)
    note = models.CharField(verbose_name='Note', null=True, blank=True)
    priority = models.CharField(verbose_name='Priority', null=True, blank=True, default="Normal")
    is_resolved = models.CharField(verbose_name='Is Resolved', null=True, blank=True, default = False)
    created_at = models.DateTimeField(verbose_name='Created At', null=True, blank=True)
    updated_at = models.DateTimeField(verbose_name="updated at", null= True)

    status = models.CharField(verbose_name='Status', null=True, blank=True, default="Active")

    def __str__(self):
        return "%s" % str(self.id) +"--ROOM ID-->"+str(self.room)
    
class ChatConversion(models.Model):
    user = models.ForeignKey(CustomerDetail,verbose_name = 'User', null=True, blank = True, on_delete=models.CASCADE)
    admin = models.ForeignKey(AdminDetail, verbose_name = 'Admin', null=True, blank = True, on_delete=models.SET_NULL)
    chat_agent = models.ForeignKey(ChatAgentDetail, verbose_name = 'Agent', null=True, blank = True, on_delete=models.CASCADE)
    room = models.ForeignKey(ChatRoom ,verbose_name='Room ID', null=True, blank=True, on_delete=models.CASCADE)
    message = models.CharField(verbose_name='Message', null=True, blank=True)
    message_french = models.CharField(verbose_name='Message French', null=True, blank=True)
    message_type = models.CharField(verbose_name='Message Type', null=True, blank=True)
    send_by = models.CharField(verbose_name='Send By', null=True, blank=True)
    product_id = models.IntegerField(null=True, blank=True)

    file = models.FileField(upload_to='chat/files', verbose_name='File', null=True, blank=True,
                        validators=[validators.validate_file_extension_image])
    file_type = models.CharField(verbose_name='File Type', null=True, blank=True)

    create_at = models.DateTimeField(verbose_name="Created At", null=True, blank=True)
    status = models.CharField(verbose_name='Status', null=True, blank=True, default='Unseen')

    def __str__(self):
        return "%s" % str(self.id) +"--ROOM ID-->"+str(self.room)
    

class AgentInChatRoomHistory(models.Model):
    room = models.ForeignKey(ChatRoom, verbose_name='Room ID', blank=True, null=True, on_delete=models.CASCADE)
    agent = models.ForeignKey(ChatAgentDetail, verbose_name='Agent ID', blank=True, null=True, on_delete=models.CASCADE)
    assigned_date = models.DateTimeField(verbose_name='Assigned Date', null=True, blank=True)
    unassigned_date = models.DateTimeField(verbose_name='Unassigned Date', null=True, blank=True)

    def __str__(self):
        return "%s" % str(self.id)+"--room-->"+str(self.agent)
    