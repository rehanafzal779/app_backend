from rest_framework import serializers
import json
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer with enhanced fields for permanent storage:
    - Uses database fields (title, status, expires_at, etc.) when available
    - Falls back to message JSON for backward compatibility
    """
    title = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    data = serializers.SerializerMethodField()
    
    class Meta: 
        model = Notification
        fields = [
            'notification_id',
            'recipient_type',
            'recipient_id',
            'message',
            'title',
            'type',
            'data',
            'is_read',
            'created_at',
            # ✅ New fields
            'status',
            'expires_at',
            'task_number',
            'accepted_at',
            'report_id',
        ]
        read_only_fields = ['notification_id', 'created_at']
    
    def get_title(self, obj):
        """Get title from database field, fallback to message JSON"""
        # ✅ Priority: database field > message JSON
        if obj.title:
            return obj.title
        try:
            if obj.message:
                message_data = json.loads(obj.message)
                return message_data.get('title') or message_data.get('message', 'Notification')
        except (json.JSONDecodeError, TypeError, AttributeError):
            pass
        return 'Notification'
    
    def get_type(self, obj):
        """Extract type from message JSON"""
        try:
            if obj.message:
                message_data = json.loads(obj.message)
                notification_type = message_data.get('type', 'general')
                # Map backend types to frontend types
                type_map = {
                    'report_available': 'task_assignment',  # Worker
                    'report_assigned': 'report_assigned',  # Citizen
                    'report_declined': 'report_rejected',  # Citizen
                    'report_resolved': 'report_resolved',  # Citizen
                    'report_in_progress': 'report_in_progress',  # Citizen
                    'feedback': 'feedback_received',  # Worker - feedback received
                }
                return type_map.get(notification_type, notification_type)
        except (json.JSONDecodeError, TypeError, AttributeError):
            pass
        return 'general'
    
    def get_data(self, obj):
        """Parse message JSON as data, merge with database fields"""
        data = {}
        try:
            if obj.message:
                data = json.loads(obj.message)
        except (json.JSONDecodeError, TypeError, AttributeError):
            pass
        
        # ✅ Merge database fields into data for frontend
        if obj.report_id:
            data['report_id'] = obj.report_id
        if obj.expires_at:
            data['expires_at'] = obj.expires_at.isoformat()
        if obj.status:
            data['status'] = obj.status
        if obj.task_number:
            data['task_number'] = obj.task_number
        if obj.accepted_at:
            data['accepted_at'] = obj.accepted_at.isoformat()
        
        return data


class SendNotificationSerializer(serializers.Serializer):
    """For POST /api/workers/{id}/notify/"""
    title = serializers.CharField(max_length=255, required=False, default='Notification')
    body = serializers.CharField(required=True)

    def validate_body(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Message body cannot be empty")
        return value.strip()