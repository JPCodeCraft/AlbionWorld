#!/usr/bin/env python3
"""
Parallel Image Processor with Flexible Transformations

Converts PNG images to WebP format with optional rotations, flips, resizing, and compression.
Processes images in parallel for maximum performance.

Usage:
  image_processor.py <folder_path> [--rotate ANGLE] [--flip {horizontal,vertical,both}] 
                   [--quality QUALITY] [--scale SCALE] [--delete] [--workers NUM]

Options:
  <folder_path>          Path to folder containing PNG images
  --rotate ANGLE         Rotate images by specified angle in degrees (e.g. 45)
  --flip {horizontal,vertical,both}  Flip images horizontally, vertically, or both
  --quality QUALITY      WebP quality (0-100, lower=smaller) [default: 75]
  --scale SCALE          Scaling factor (0.1-1.0) [default: 0.5]
  --delete               Delete original PNG files after processing
  --workers NUM          Number of parallel workers [default: all CPUs]

Examples:
  # Rotate 45 degrees and vertical flip
  image_processor.py ./images --rotate 45 --flip vertical --quality 80
  
  # Horizontal flip only
  image_processor.py ./images --flip horizontal
  
  # Scale to 30% with max compression
  image_processor.py ./images --scale 0.3 --quality 50 --delete
  
  # Convert without transformations
  image_processor.py ./images
"""

import os
import sys
from PIL import Image
import argparse
from multiprocessing import Pool, cpu_count

def process_single_image(args):
    (filename, folder_path, quality, scale_factor, 
     delete_originals, rotate_angle, flip_mode) = args
     
    if not filename.lower().endswith('.png'):
        return

    file_path = os.path.join(folder_path, filename)
    webp_path = os.path.join(folder_path, f"{os.path.splitext(filename)[0]}.webp")
    
    try:
        with Image.open(file_path) as img:
            # Preserve transparency
            if img.mode in ('P', 'RGB'):
                img = img.convert('RGBA')
                
            current_image = img.copy()

            # Apply rotation if specified
            if rotate_angle is not None:
                current_image = current_image.rotate(
                    rotate_angle,
                    expand=True,
                    resample=Image.BICUBIC,
                    fillcolor=(0, 0, 0, 0)  # Transparent background
                )

            # Apply flipping if specified
            if flip_mode:
                flip_methods = {
                    'horizontal': Image.FLIP_LEFT_RIGHT,
                    'vertical': Image.FLIP_TOP_BOTTOM,
                    'both': (Image.FLIP_LEFT_RIGHT, Image.FLIP_TOP_BOTTOM)
                }
                
                flips = flip_methods[flip_mode]
                if isinstance(flips, tuple):
                    for method in flips:
                        current_image = current_image.transpose(method)
                else:
                    current_image = current_image.transpose(flips)

            # Calculate new dimensions
            new_width = int(current_image.width * scale_factor)
            new_height = int(current_image.height * scale_factor)
            
            # High-quality resizing
            resized = current_image.resize(
                (new_width, new_height),
                resample=Image.LANCZOS
            )
            
            # Save as optimized WebP
            resized.save(
                webp_path,
                format='WEBP',
                quality=quality,
                method=6,
                lossless=False,
                exact=True  # Preserve transparency
            )
            
            if delete_originals:
                os.remove(file_path)
            
            return (filename, os.path.getsize(file_path), os.path.getsize(webp_path))

    except Exception as e:
        return (filename, str(e))

def process_images(folder_path, quality=75, scale_factor=0.5, 
                  delete_originals=False, workers=cpu_count(),
                  rotate_angle=None, flip_mode=None):
    files = []
    for root, _, filenames in os.walk(folder_path):
        for f in filenames:
            if f.lower().endswith('.png'):
                files.append((f, root, quality, scale_factor, delete_originals, rotate_angle, flip_mode))
    
    with Pool(processes=workers) as pool:
        results = pool.imap_unordered(process_single_image, files)
        
        for result in results:
            if not result:
                continue
            if isinstance(result[1], str):  # Error case
                print(f"Error processing {result[0]}: {result[1]}")
            else:
                filename, orig_size, new_size = result
                print(f"Processed {filename}: {orig_size/1024:.1f}KB → {new_size/1024:.1f}KB")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Optimized image conversion tool",
                                    formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('folder_path', help="Directory containing PNG images")
    parser.add_argument('--rotate', type=float, metavar='ANGLE',
                       help="Rotation angle in degrees (e.g. 45)")
    parser.add_argument('--flip', choices=['horizontal', 'vertical', 'both'],
                       help="Flip direction: horizontal, vertical, or both")
    parser.add_argument('--quality', type=int, default=75,
                       help="WebP quality (0-100) [default: %(default)s]")
    parser.add_argument('--scale', type=float, default=0.5,
                       help="Scaling factor (0.1-1.0) [default: %(default)s]")
    parser.add_argument('--delete', action='store_true',
                       help="Delete original PNG files after conversion")
    parser.add_argument('--workers', type=int, default=cpu_count(),
                       help=f"Parallel workers [default: %(default)s]")

    args = parser.parse_args()

    if not os.path.isdir(args.folder_path):
        print(f"Error: Invalid directory '{args.folder_path}'")
        sys.exit(1)

    process_images(
        args.folder_path,
        quality=args.quality,
        scale_factor=args.scale,
        delete_originals=args.delete,
        workers=args.workers,
        rotate_angle=args.rotate,
        flip_mode=args.flip
    )