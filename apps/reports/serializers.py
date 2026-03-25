from rest_framework import serializers
from .models import Report
import json
import urllib.request
import urllib.error
import ssl

# SSL context
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# Simple location cache (in-memory)
_location_cache = {}



def get_location_from_coordinates(lat, lng):
    """
    Convert coordinates to readable address
    """
    if lat is None or lng is None:
        return 'Unknown Location'
    
    try:
        lat = float(lat)
        lng = float(lng)
    except (ValueError, TypeError):
        return 'Unknown Location'
    
    cache_key = f"{lat:.6f},{lng:.6f}"
    
    # Check cache
    if cache_key in _location_cache: 
        return _location_cache[cache_key]
    
    address = None
    
    # Try Nominatim
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat={lat}&lon={lng}&zoom=18&addressdetails=1"
        req = urllib.request. Request(
            url,
            headers={
                'User-Agent': 'NeatNowApp/1.0',
                'Accept-Language': 'en'
            }
        )
        
        with urllib.request.urlopen(req, timeout=5, context=ssl_context) as response:
            data = json. loads(response.read().decode('utf-8'))
            
            if 'address' in data:
                addr = data['address']
                parts = []
                
                # Building/Landmark
                building = addr.get('building') or addr.get('amenity') or addr.get('tourism')
                if building and building != 'yes':
                    parts.append(building)
                
                # Street
                if addr.get('house_number') and addr.get('road'):
                    parts.append(f"{addr['house_number']} {addr['road']}")
                elif addr.get('road'):
                    parts.append(addr['road'])
                
                # Neighborhood
                neighborhood = addr.get('neighbourhood') or addr.get('suburb') or addr.get('quarter')
                if neighborhood:
                    parts.append(neighborhood)
                
                # City
                city = addr.get('city') or addr.get('town') or addr.get('village')
                if city:
                    parts.append(city)
                
                # Postal code
                if addr.get('postcode'):
                    parts.append(addr['postcode'])
                
                if parts:
                    address = ', '.join(parts)
    except Exception as e: 
        print(f"Nominatim error:  {e}")
    
    # Try BigDataCloud as fallback
    if not address:
        try:
            url = f"https://api.bigdatacloud.net/data/reverse-geocode-client?latitude={lat}&longitude={lng}&localityLanguage=en"
            req = urllib. request.Request(url)
            
            with urllib.request.urlopen(req, timeout=5, context=ssl_context) as response:
                data = json. loads(response.read().decode('utf-8'))
                
                parts = []
                if data.get('locality'):
                    parts.append(data['locality'])
                if data.get('city'):
                    parts.append(data['city'])
                if data.get('principalSubdivision'):
                    parts.append(data['principalSubdivision'])
                if data. get('postcode'):
                    parts.append(data['postcode'])
                
                if parts:
                    address = ', '.join(parts)
        except Exception as e: 
            print(f"BigDataCloud error:  {e}")
    
    # Local fallback for Pakistan/USA
    if not address: 
        address = get_local_fallback(lat, lng)
    
    # Cache the result
    _location_cache[cache_key] = address
    
    return address



def get_local_fallback(lat, lng):
    """Get location from local database for common areas"""
    
    # Faisalabad
    if 31.35 <= lat <= 31.75 and 72.95 <= lng <= 74.15:
        if 31.410 <= lat <= 31.430 and 73.080 <= lng <= 73.100:
            return 'D Ground, Civil Lines, Faisalabad, 38000'
        if 31.430 <= lat <= 31.470 and 73.050 <= lng <= 73.100:
            return 'Peoples Colony, Faisalabad, 38000'
        if 31.450 <= lat <= 31.500 and 73.080 <= lng <= 73.150:
            return 'Madina Town, Faisalabad, 38000'
        return 'Faisalabad, Punjab, 38000'
    
    # Islamabad
    if 33.60 <= lat <= 33.80 and 72.80 <= lng <= 73.20:
        if 33.680 <= lat <= 33.720 and 73.030 <= lng <= 73.080:
            return 'Srinagar Highway, G-9, Islamabad, 44000'
        if 33.705 <= lat <= 33.715 and 73.055 <= lng <= 73.085:
            return 'Blue Area, Islamabad, 44000'
        return 'Islamabad, ICT, 44000'
    
    # Lahore
    if 31.40 <= lat <= 31.65 and 74.20 <= lng <= 74.50:
        if 31.510 <= lat <= 31.530 and 74.330 <= lng <= 74.360:
            return 'Gulberg III, Lahore, 54660'
        return 'Lahore, Punjab, 54000'
    
    # Karachi
    if 24.80 <= lat <= 25.00 and 66.90 <= lng <= 67.20:
        return 'Karachi, Sindh, 74000'
    
    # New York
    if 40.5 <= lat <= 41.0 and -74.5 <= lng <= -73.5:
        if 40.710 <= lat <= 40.715 and -74.010 <= lng <= -74.000:
            return 'New York City Hall, 260 Broadway, Tribeca, New York'
        if 40.755 <= lat <= 40.760: 
            return 'Times Square, Manhattan, New York'
        return 'Manhattan, New York, NY 10001'
    
    return f'Location ({lat:. 4f}, {lng:.4f})'


class ReportSerializer(serializers.ModelSerializer):
    """Full report serializer with computed fields"""
    citizen_name = serializers.SerializerMethodField()
    worker_name = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()  # ✅ Computed location
    feedback = serializers.SerializerMethodField()  # ✅ Include feedback data
    
    class Meta: 
        model = Report
        fields = [
            'report_id',
            'citizen_name',
            'worker_name',
            'status',
            'ai_result',
            'waste_type',
            'ai_confidence',
            'latitude',
            'longitude',
            'location',  # ✅ This will be the readable address
            'image_before',
            'image_after',
            'submitted_at',
            'assigned_at',
            'accepted_at',  # ✅ When worker accepts the report
            'started_at',  # ✅ When worker starts the task (status changes to In Progress)
            'resolved_at',
            'feedback',  # ✅ Feedback data (rating, comment)
        ]
    
    def get_citizen_name(self, obj):
        if obj.citizen_id:
            return obj.citizen_id. name
        return 'Unknown'
    
    def get_worker_name(self, obj):
        if obj.worker_id and hasattr(obj.worker_id, 'worker_id') and obj.worker_id.worker_id:
            return obj.worker_id. worker_id. name
        return None
    
    def get_location(self, obj):
        """Convert coordinates to readable address"""
        return get_location_from_coordinates(obj. latitude, obj.longitude)
    def get_feedback(self, obj):
        # Return whatever you want for feedback
        # Example:
        if hasattr(obj, 'feedback') and obj.feedback is not None:
            return obj.feedback
        return None

class ReportListSerializer(serializers. ModelSerializer):
    """Lightweight serializer for list view with optimized task number calculation"""
    citizen_name = serializers.SerializerMethodField()
    worker_name = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()  # ✅ Computed location
    task_number = serializers.SerializerMethodField()  # ✅ Task number based on acceptance order (optimized)
    after_image_url = serializers.SerializerMethodField()  # ✅ Convert image_after to after_image_url for frontend
    feedback = serializers.SerializerMethodField()  # ✅ Include feedback data
    
    # ✅ Class-level cache for task numbers (shared across all instances in a request)
    _task_number_cache = {}
    _cache_initialized = False
    
    class Meta: 
        model = Report
        fields = [
            'report_id',
            'citizen_name',
            'worker_name',
            'status',
            'ai_result',
            'waste_type',
            'latitude',
            'longitude',
            'location',  # ✅ Readable address
            'image_before',
            'image_after',  # ✅ After cleanup image (required for resolved reports) - kept for backward compatibility
            'after_image_url',  # ✅ Frontend-friendly field name
            'submitted_at',
            'accepted_at',  # ✅ When worker accepts the report
            'started_at',  # ✅ When worker starts the task (status changes to In Progress)
            'resolved_at',  # ✅ When report is resolved
            'task_number',  # ✅ Task number (1, 2, 3... based on acceptance order)
            'feedback',  # ✅ Feedback data (rating, comment)
        ]
    
    def get_citizen_name(self, obj):
        if obj.citizen_id:
            return obj. citizen_id.name
        return 'Unknown'
    
    def get_worker_name(self, obj):
        if obj.worker_id and hasattr(obj.worker_id, 'worker_id') and obj.worker_id.worker_id:
            return obj.worker_id.worker_id. name
        return None
    
    def get_location(self, obj):
        """Convert coordinates to readable address"""
        return get_location_from_coordinates(obj. latitude, obj.longitude)
    
    def get_after_image_url(self, obj):
        """Convert image_after ImageField to URL for frontend"""
        if obj.image_after:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image_after.url)
            return obj.image_after.url
        return None
    
    def get_feedback(self, obj):
        """Get feedback data for this report"""
        try:
            if hasattr(obj, 'feedback') and obj.feedback:
                return {
                    'rating': obj.feedback.rating,
                    'comment': obj.feedback.comment,
                    'created_at': obj.feedback.created_at.isoformat() if obj.feedback.created_at else None,
                }
        except Exception:
            pass
        return None
    
    def get_task_number(self, obj):
        """Calculate task number based on acceptance order (OPTIMIZED - bulk calculation)"""
        if not obj.worker_id or not obj.accepted_at:
            return None
        
        # ✅ Use cache key based on worker_id (get the actual worker instance ID)
        # obj.worker_id is a Worker instance, we need its primary key
        worker_pk = obj.worker_id.pk if obj.worker_id else None
        if not worker_pk:
            return None
        cache_key = f'worker_{worker_pk}'
        
        # ✅ Initialize cache for this worker if not already done
        if cache_key not in self._task_number_cache:
            from apps.reports.models import Report
            # ✅ Single query to get all accepted reports for this worker, ordered by acceptance
            accepted_reports = Report.objects.filter(
                worker_id=obj.worker_id,
                accepted_at__isnull=False,
                status__in=['Assigned', 'In Progress', 'Resolved']
            ).order_by('accepted_at').values_list('report_id', flat=True)
            
            # ✅ Create a dictionary mapping report_id to task_number (1-based index)
            task_numbers = {}
            for index, report_id in enumerate(accepted_reports, start=1):
                task_numbers[report_id] = index
            
            # ✅ Store in cache
            self._task_number_cache[cache_key] = task_numbers
        
        # ✅ Get task number from cache
        task_numbers = self._task_number_cache[cache_key]
        return task_numbers.get(obj.report_id)


class ReportCreateSerializer(serializers. ModelSerializer):
    """Serializer for creating reports"""
    
    class Meta:
        model = Report
        fields = [
            'citizen_id',
            'waste_type',
            'latitude',
            'longitude',
            'image_before',
            'ai_result',
            'ai_confidence',
        ]
    
    def create(self, validated_data):
        # Set default values
        validated_data.setdefault('status', 'Pending')
        validated_data.setdefault('ai_result', 'Unverified')
        return super().create(validated_data)


class ReportUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating reports"""
    
    class Meta: 
        model = Report
        fields = [
            'status',
            'worker_id',
            'waste_type',
            'image_after',
            'ai_result',
            'ai_confidence',
        ]