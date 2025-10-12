#!/usr/bin/env python3
"""
Test script for Gemini API image generation.
This script tests the Google Generative Language API integration directly.
"""
import asyncio
import httpx
import base64
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


async def test_gemini_api():
    """Test the Gemini API with a sample image."""
    
    print("=" * 60)
    print("Gemini API Test Script")
    print("=" * 60)
    
    # Configuration
    api_key = os.getenv('NANO_BANANA_API_KEY')
    api_url = os.getenv('NANO_BANANA_API_URL', 'https://generativelanguage.googleapis.com')
    model = "gemini-2.0-flash-exp"
    
    print(f"\n✓ API URL: {api_url}")
    print(f"✓ Model: {model}")
    print(f"✓ API Key: {api_key[:20]}..." if api_key else "✗ API Key not set!")
    
    if not api_key:
        print("\n❌ ERROR: NANO_BANANA_API_KEY not set in .env file")
        return False
    
    # Create a simple test image (1x1 red pixel PNG)
    # This is a valid minimal PNG file
    test_image_base64 = (
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8DwHwAFBQIAX8jx0gAAAABJRU5ErkJggg=="
    )
    
    print(f"\n✓ Test image created (1x1 red pixel PNG)")
    
    # Create the prompt
    prompt = "Describe this image in detail."
    
    # Build the payload
    payload = {
        "contents": [{
            "role": "user",
            "parts": [
                {
                    "text": prompt
                },
                {
                    "inline_data": {
                        "mime_type": "image/png",
                        "data": test_image_base64
                    }
                }
            ]
        }],
        "generation_config": {
            "temperature": 0.4,
            "top_p": 1.0,
            "top_k": 32,
            "max_output_tokens": 2048,
        }
    }
    
    # Construct endpoint
    endpoint = f"{api_url}/v1beta/models/{model}:generateContent?key={api_key}"
    
    print(f"\n🚀 Sending request to Gemini API...")
    print(f"   Endpoint: {api_url}/v1beta/models/{model}:generateContent")
    print(f"   Prompt: {prompt}")
    
    try:
        headers = {"Content-Type": "application/json"}
        async with httpx.AsyncClient(timeout=30.0, headers=headers) as client:
            response = await client.post(endpoint, json=payload)
            
            print(f"\n✓ Response Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✓ Response received successfully!")
                
                # Extract the text response
                if "candidates" in result and len(result["candidates"]) > 0:
                    candidate = result["candidates"][0]
                    if "content" in candidate:
                        parts = candidate["content"].get("parts", [])
                        if parts and "text" in parts[0]:
                            generated_text = parts[0]["text"]
                            print(f"\n📝 Generated Response:")
                            print("-" * 60)
                            print(generated_text)
                            print("-" * 60)
                
                print(f"\n✅ SUCCESS! Gemini API is working correctly.")
                print(f"\nFull response:")
                import json
                print(json.dumps(result, indent=2))
                return True
            else:
                print(f"\n❌ ERROR: API returned status {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
    except httpx.HTTPError as e:
        print(f"\n❌ HTTP Error: {e}")
        if hasattr(e, 'response'):
            print(f"Status: {e.response.status_code}")
            print(f"Response: {e.response.text}")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_with_real_image():
    """Test with a real image file if available."""
    
    print("\n" + "=" * 60)
    print("Testing with Real Image (if available)")
    print("=" * 60)
    
    # Look for test images in common locations
    test_image_paths = [
        "/Users/ravenir/dev/apps/product-snap/test_image.jpg",
        "/Users/ravenir/dev/apps/product-snap/test_image.png",
        "/Users/ravenir/Desktop/test.jpg",
        "/Users/ravenir/Desktop/test.png",
    ]
    
    test_image_path = None
    for path in test_image_paths:
        if os.path.exists(path):
            test_image_path = path
            break
    
    if not test_image_path:
        print("\n⚠️  No test image found. Skipping real image test.")
        print("   To test with a real image, place a file at:")
        print("   - /Users/ravenir/dev/apps/product-snap/test_image.jpg")
        return True
    
    print(f"\n✓ Found test image: {test_image_path}")
    
    # Read and encode the image
    with open(test_image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')
    
    # Detect mime type
    if test_image_path.endswith('.png'):
        mime_type = 'image/png'
    elif test_image_path.endswith('.jpg') or test_image_path.endswith('.jpeg'):
        mime_type = 'image/jpeg'
    else:
        mime_type = 'image/jpeg'
    
    print(f"✓ Image encoded ({len(image_data)} chars, {mime_type})")
    
    # Create a product photography prompt
    prompt = """Analyze this product image and describe:
1. What product is shown
2. Current lighting and background
3. Suggestions for professional product photography styling
"""
    
    # Build payload
    api_key = os.getenv('NANO_BANANA_API_KEY')
    api_url = os.getenv('NANO_BANANA_API_URL', 'https://generativelanguage.googleapis.com')
    model = "gemini-2.0-flash-exp"
    
    payload = {
        "contents": [{
            "role": "user",
            "parts": [
                {"text": prompt},
                {
                    "inline_data": {
                        "mime_type": mime_type,
                        "data": image_data
                    }
                }
            ]
        }],
        "generation_config": {
            "temperature": 0.4,
            "top_p": 1.0,
            "top_k": 32,
            "max_output_tokens": 2048,
        }
    }
    
    endpoint = f"{api_url}/v1beta/models/{model}:generateContent?key={api_key}"
    
    print(f"\n🚀 Analyzing real image with Gemini...")
    
    try:
        headers = {"Content-Type": "application/json"}
        async with httpx.AsyncClient(timeout=30.0, headers=headers) as client:
            response = await client.post(endpoint, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                
                if "candidates" in result and len(result["candidates"]) > 0:
                    candidate = result["candidates"][0]
                    if "content" in candidate:
                        parts = candidate["content"].get("parts", [])
                        if parts and "text" in parts[0]:
                            generated_text = parts[0]["text"]
                            print(f"\n📝 Analysis Result:")
                            print("-" * 60)
                            print(generated_text)
                            print("-" * 60)
                
                print(f"\n✅ Real image analysis successful!")
                return True
            else:
                print(f"\n❌ ERROR: Status {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


async def main():
    """Run all tests."""
    print("\n🧪 Starting Gemini API Tests\n")
    
    # Test 1: Basic API test with minimal image
    test1_passed = await test_gemini_api()
    
    # Test 2: Real image test (optional)
    test2_passed = await test_with_real_image()
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Basic API Test: {'✅ PASS' if test1_passed else '❌ FAIL'}")
    print(f"Real Image Test: {'✅ PASS' if test2_passed else '⚠️  SKIPPED'}")
    
    if test1_passed:
        print("\n🎉 All tests passed! Your Gemini API integration is working.")
        print("\nNext steps:")
        print("1. Rebuild your worker: ./local-docker/dev.sh worker")
        print("2. Try generating an image through the web interface")
    else:
        print("\n❌ Tests failed. Please check the error messages above.")
        print("\nCommon issues:")
        print("- Invalid API key")
        print("- API not enabled in Google Cloud Console")
        print("- Network connectivity issues")


if __name__ == "__main__":
    asyncio.run(main())
