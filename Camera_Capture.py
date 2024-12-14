import numpy as np
import pyk4a
from pyk4a import Config, PyK4A
import time
from decouple import config
Filename = config("FileName")
def save_ply_fast(filename, points, colors):
    # Filter out points with invalid depth (Z <= 0)
    valid_mask = points[:, 2] > 0
    valid_points = points[valid_mask]
    valid_colors = colors[valid_mask]

    # Combine points and colors into a single array
    ply_data = np.hstack((valid_points, valid_colors)).astype(np.float32)

    # Prepare PLY header
    num_points = ply_data.shape[0]
    header = f"""ply
format ascii 1.0
element vertex {num_points}
property float x
property float y
property float z
property uchar red
property uchar green
property uchar blue
end_header
"""

    # Write header and data to file
    with open(filename, 'w') as f:
        f.write(header)
        np.savetxt(f, ply_data, fmt="%.3f %.3f %.3f %d %d %d")

    print(f"Point cloud saved to {filename}")

def main():
    k4a = PyK4A(
        Config(
            color_resolution=pyk4a.ColorResolution.RES_720P,
            camera_fps=pyk4a.FPS.FPS_5,
            depth_mode=pyk4a.DepthMode.WFOV_2X2BINNED,
            synchronized_images_only=True,
        )
    )
    k4a.start()

    try:
        while True:
            # Capture frames
            capture = k4a.get_capture()
            if capture.depth is not None and capture.color is not None:
                # Convert depth image to 3D point cloud
                points = capture.depth_point_cloud.reshape((-1, 3))
                colors = capture.transformed_color[..., (2, 1, 0)].reshape((-1, 3))

                # Save the point cloud to a .ply file with a unique name
                filename = f"./Picture/{Filename}.ply"
                save_ply_fast(filename, points, colors)

                

                # Optional: Add a delay to control capture frequency
                time.sleep(0.5)

    except KeyboardInterrupt:
        print("Stopping capture loop...")

    finally:
        k4a.stop()

if __name__ == "__main__":
    main()