import os
import logging
import queue
import numpy as np
import pyk4a
from pyk4a import Config, PyK4A
from threading import Thread, Event
from decouple import config

# Read file name from .env
FILE_NAME = config("FileName")

# Setup logging
logging.basicConfig(level=logging.INFO)

# Stop event for clean shutdown
stop_event = Event()

def save_ply_binary(filename, points, colors):
    """Save the point cloud as a binary PLY file."""
    valid_mask = points[:, 2] > 0
    valid_points = points[valid_mask]
    valid_colors = colors[valid_mask]

    # Combine points and colors
    ply_data = np.hstack((valid_points, valid_colors)).astype(np.float32)

    # PLY header for binary format
    header = f"""ply
format binary_little_endian 1.0
element vertex {ply_data.shape[0]}
property float x
property float y
property float z
property uchar red
property uchar green
property uchar blue
end_header
"""

    # Write binary PLY
    with open(filename, 'wb') as f:
        f.write(header.encode('utf-8'))
        f.write(ply_data.astype([('x', 'f4'), ('y', 'f4'), ('z', 'f4'),
                                 ('r', 'u1'), ('g', 'u1'), ('b', 'u1')]).tobytes())


def capture_and_process(k4a, save_queue):
    while not stop_event.is_set():
        capture = k4a.get_capture()
        if capture.depth is not None and capture.color is not None:
            points = capture.depth_point_cloud.reshape((-1, 3))
            colors = capture.transformed_color[..., (2, 1, 0)].reshape((-1, 3))
            save_queue.put((points, colors))


def save_worker(save_queue):
    os.makedirs("./Picture", exist_ok=True)
    while not stop_event.is_set():
        try:
            points, colors = save_queue.get(timeout=1)
            filename = f"./Picture/{FILE_NAME}.ply"
            save_ply_binary(filename, points, colors)
            logging.info(f"Saved point cloud to {filename}")
        except queue.Empty:
            continue


def main():
    # Initialize Kinect device
    k4a = PyK4A(
        Config(
            color_resolution=pyk4a.ColorResolution.RES_720P,
            camera_fps=pyk4a.FPS.FPS_15,  # Set to 15 FPS
            depth_mode=pyk4a.DepthMode.WFOV_2X2BINNED,
            synchronized_images_only=True,
        )
    )
    k4a.start()

    # Thread-safe queue to store frames for saving
    save_queue = queue.Queue(maxsize=15)  # Buffer for 1 second of frames

    # Start capture and save threads
    capture_thread = Thread(target=capture_and_process, args=(k4a, save_queue), daemon=True)
    save_thread = Thread(target=save_worker, args=(save_queue,), daemon=True)

    capture_thread.start()
    save_thread.start()

    try:
        while not stop_event.is_set():
            pass  # Main thread keeps running
    except KeyboardInterrupt:
        print("Stopping capture loop...")
        stop_event.set()

    finally:
        k4a.stop()
        logging.info("Kinect stopped.")

if __name__ == "__main__":
    main()