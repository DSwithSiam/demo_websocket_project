"""
Custom Middleware for User Activity Tracking

This middleware tracks user activity and logs requests for authenticated users.
"""

import logging
from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone

logger = logging.getLogger(__name__)


class UserActivityMiddleware(MiddlewareMixin):
    """
    Middleware to track user activity and log requests.
    
    Features:
    - Logs authenticated user requests
    - Tracks user activity timestamps
    - Can be extended for analytics and monitoring
    """
    
    def process_request(self, request):
        """
        Process incoming requests and log user activity.
        
        Args:
            request: HTTP request object
        """
        # Check if user is authenticated
        if hasattr(request, 'user') and request.user.is_authenticated:
            # Log user activity
            logger.info(
                f"User Activity: {request.user.email} | "
                f"Method: {request.method} | "
                f"Path: {request.path} | "
                f"Time: {timezone.now()}"
            )
            
            # You can extend this to update last_activity field
            # if you add that field to CustomUser model
            # request.user.last_activity = timezone.now()
            # request.user.save(update_fields=['last_activity'])
        
        return None
    
    def process_response(self, request, response):
        """
        Process outgoing responses.
        
        Args:
            request: HTTP request object
            response: HTTP response object
        
        Returns:
            HTTP response object
        """
        # You can add additional logging or processing here
        return response
