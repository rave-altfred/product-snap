#!/usr/bin/env python3
"""
Test script to debug HEIC image decoding.
Run this directly on macOS to test different HEIC decoding methods.

Usage:
    python3 test_heic.py <path_to_heic_file>
"""

import sys
import subprocess
from pathlib import Path

def test_pillow_heif(heic_path):
    """Test using pillow_heif library"""
    print("\n" + "="*60)
    print("Testing with pillow_heif...")
    print("="*60)
    try:
        import pillow_heif
        from pillow_heif import register_heif_opener
        from PIL import Image
        
        # Register HEIF opener
        register_heif_opener()
        
        # Try to open with PIL
        try:
            img = Image.open(heic_path)
            print(f"✓ PIL.Image.open() SUCCESS")
            print(f"  Format: {img.format}")
            print(f"  Mode: {img.mode}")
            print(f"  Size: {img.size}")
            return True
        except Exception as e:
            print(f"✗ PIL.Image.open() FAILED: {e}")
        
        # Try with pillow_heif.open_heif
        try:
            with open(heic_path, 'rb') as f:
                file_content = f.read()
            heif_file = pillow_heif.open_heif(file_content, convert_hdr_to_8bit=False, bgr_mode=False)
            print(f"✓ pillow_heif.open_heif() SUCCESS")
            print(f"  Mode: {heif_file.mode}")
            print(f"  Size: {heif_file.size}")
            return True
        except Exception as e:
            print(f"✗ pillow_heif.open_heif() FAILED: {e}")
        
        # Try with pillow_heif.read_heif
        try:
            heif_file = pillow_heif.read_heif(file_content)
            print(f"✓ pillow_heif.read_heif() SUCCESS")
            print(f"  Mode: {heif_file.mode}")
            print(f"  Size: {heif_file.size}")
            return True
        except Exception as e:
            print(f"✗ pillow_heif.read_heif() FAILED: {e}")
            
    except ImportError:
        print("✗ pillow_heif not installed")
        print("  Install with: pip3 install pillow-heif")
    
    return False

def test_imagemagick(heic_path):
    """Test using ImageMagick command line"""
    print("\n" + "="*60)
    print("Testing with ImageMagick...")
    print("="*60)
    
    # Check if ImageMagick is installed
    try:
        result = subprocess.run(['convert', '-version'], capture_output=True, text=True)
        print(f"✓ ImageMagick installed")
        print(f"  Version: {result.stdout.split()[2]}")
    except FileNotFoundError:
        print("✗ ImageMagick not installed")
        print("  Install with: brew install imagemagick")
        return False
    
    # Try to identify the image
    try:
        result = subprocess.run(['identify', str(heic_path)], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"✓ ImageMagick identify SUCCESS")
            print(f"  {result.stdout.strip()}")
            return True
        else:
            print(f"✗ ImageMagick identify FAILED")
            print(f"  {result.stderr.strip()}")
    except subprocess.TimeoutExpired:
        print("✗ ImageMagick identify TIMEOUT")
    except Exception as e:
        print(f"✗ ImageMagick identify ERROR: {e}")
    
    return False

def test_heif_convert(heic_path):
    """Test using heif-convert from libheif"""
    print("\n" + "="*60)
    print("Testing with heif-convert (libheif)...")
    print("="*60)
    
    try:
        result = subprocess.run(['heif-convert', '--version'], capture_output=True, text=True)
        print(f"✓ heif-convert installed")
    except FileNotFoundError:
        print("✗ heif-convert not installed")
        print("  Install with: brew install libheif")
        return False
    
    # Try to convert
    output_path = Path(heic_path).with_suffix('.test.jpg')
    try:
        result = subprocess.run(
            ['heif-convert', str(heic_path), str(output_path)],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and output_path.exists():
            print(f"✓ heif-convert SUCCESS")
            print(f"  Output: {output_path}")
            output_path.unlink()  # Clean up
            return True
        else:
            print(f"✗ heif-convert FAILED")
            print(f"  {result.stderr.strip()}")
    except subprocess.TimeoutExpired:
        print("✗ heif-convert TIMEOUT")
    except Exception as e:
        print(f"✗ heif-convert ERROR: {e}")
    
    return False

def test_sips(heic_path):
    """Test using macOS sips command"""
    print("\n" + "="*60)
    print("Testing with macOS sips...")
    print("="*60)
    
    # sips is always available on macOS
    output_path = Path(heic_path).with_suffix('.test.jpg')
    try:
        result = subprocess.run(
            ['sips', '-s', 'format', 'jpeg', str(heic_path), '--out', str(output_path)],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and output_path.exists():
            print(f"✓ sips conversion SUCCESS")
            print(f"  Output: {output_path}")
            # Get info
            info_result = subprocess.run(['sips', '-g', 'all', str(heic_path)], capture_output=True, text=True)
            print(f"  Info: {info_result.stdout[:200]}")
            output_path.unlink()  # Clean up
            return True
        else:
            print(f"✗ sips conversion FAILED")
            print(f"  {result.stderr.strip()}")
    except subprocess.TimeoutExpired:
        print("✗ sips conversion TIMEOUT")
    except Exception as e:
        print(f"✗ sips conversion ERROR: {e}")
    
    return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 test_heic.py <path_to_heic_file>")
        sys.exit(1)
    
    heic_path = Path(sys.argv[1])
    
    if not heic_path.exists():
        print(f"Error: File not found: {heic_path}")
        sys.exit(1)
    
    print(f"\nTesting HEIC file: {heic_path}")
    print(f"File size: {heic_path.stat().st_size:,} bytes")
    
    results = []
    results.append(("pillow_heif", test_pillow_heif(heic_path)))
    results.append(("ImageMagick", test_imagemagick(heic_path)))
    results.append(("heif-convert", test_heif_convert(heic_path)))
    results.append(("macOS sips", test_sips(heic_path)))
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    for method, success in results:
        status = "✓ SUCCESS" if success else "✗ FAILED"
        print(f"{method:20} {status}")
    
    # Recommendation
    print("\n" + "="*60)
    print("RECOMMENDATION")
    print("="*60)
    
    if results[3][1]:  # macOS sips
        print("✓ Use macOS 'sips' command - most reliable on macOS")
    elif results[1][1]:  # ImageMagick
        print("✓ Use ImageMagick - good cross-platform support")
    elif results[2][1]:  # heif-convert
        print("✓ Use heif-convert - direct libheif tool")
    elif results[0][1]:  # pillow_heif
        print("✓ Use pillow_heif - Python library")
    else:
        print("✗ No working method found. This HEIC file may have issues.")

if __name__ == '__main__':
    main()
