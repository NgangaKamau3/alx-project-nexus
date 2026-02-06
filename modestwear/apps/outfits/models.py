from django.db import models
from django.contrib.auth import get_user_model
from apps.catalog.models import Product

User = get_user_model()

class Outfit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='outfits')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.name}"

class OutfitItem(models.Model):
    outfit = models.ForeignKey(Outfit, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    position = models.PositiveIntegerField(default=0)  # For ordering items in outfit
    
    class Meta:
        ordering = ['position']
        unique_together = ['outfit', 'product']
    
    def __str__(self):
        return f"{self.outfit.name} - {self.product.name}"
