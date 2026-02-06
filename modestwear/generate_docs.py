#!/usr/bin/env python
"""
Generate static API documentation files
"""
import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from drf_yasg.generators import OpenAPISchemaGenerator
from drf_yasg.openapi import Info
from drf_yasg import openapi
import json

def generate_openapi_json():
    """Generate OpenAPI JSON schema"""
    generator = OpenAPISchemaGenerator(
        info=Info(
            title="ModestWear API",
            default_version='v1',
            description="ModestWear Fashion E-commerce API Documentation",
        ),
        patterns=None,
    )
    
    schema = generator.get_schema(request=None, public=True)
    
    # Save as JSON
    with open('api_schema.json', 'w') as f:
        json.dump(schema, f, indent=2, default=str)
    
    print("✅ Generated: api_schema.json")
    return schema

def generate_swagger_html():
    """Generate standalone Swagger HTML"""
    html_content = '''<!DOCTYPE html>
<html>
<head>
    <title>ModestWear API Documentation</title>
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@3.25.0/swagger-ui.css" />
    <style>
        html { box-sizing: border-box; overflow: -moz-scrollbars-vertical; overflow-y: scroll; }
        *, *:before, *:after { box-sizing: inherit; }
        body { margin:0; background: #fafafa; }
    </style>
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@3.25.0/swagger-ui-bundle.js"></script>
    <script>
        SwaggerUIBundle({
            url: './api_schema.json',
            dom_id: '#swagger-ui',
            deepLinking: true,
            presets: [
                SwaggerUIBundle.presets.apis,
                SwaggerUIBundle.presets.standalone
            ],
            plugins: [
                SwaggerUIBundle.plugins.DownloadUrl
            ],
            layout: "StandaloneLayout"
        });
    </script>
</body>
</html>'''
    
    with open('api_docs.html', 'w') as f:
        f.write(html_content)
    
    print("✅ Generated: api_docs.html")

def generate_redoc_html():
    """Generate standalone ReDoc HTML"""
    html_content = '''<!DOCTYPE html>
<html>
<head>
    <title>ModestWear API Documentation</title>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">
    <style>
        body { margin: 0; padding: 0; }
    </style>
</head>
<body>
    <redoc spec-url='./api_schema.json'></redoc>
    <script src="https://cdn.jsdelivr.net/npm/redoc@2.0.0/bundles/redoc.standalone.js"></script>
</body>
</html>'''
    
    with open('api_redoc.html', 'w') as f:
        f.write(html_content)
    
    print("✅ Generated: api_redoc.html")

if __name__ == '__main__':
    print("🔧 Generating API Documentation...")
    generate_openapi_json()
    generate_swagger_html()
    generate_redoc_html()
    print("\n📁 Files generated:")
    print("   - api_schema.json (OpenAPI schema)")
    print("   - api_docs.html (Swagger UI)")
    print("   - api_redoc.html (ReDoc)")
    print("\n📤 Send these files to your frontend developer!")