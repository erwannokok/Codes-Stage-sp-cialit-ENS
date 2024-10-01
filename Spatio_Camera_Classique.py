import os
import numpy as np
import matplotlib.pyplot as plt
from tkinter import Tk, filedialog, simpledialog
from PIL import Image
from mpl_toolkits.mplot3d import Axes3D
from sklearn.cluster import DBSCAN

def select_folder():
    root = Tk()
    root.withdraw()  # Hide the main window
    folder_selected = filedialog.askdirectory()
    root.destroy()
    return folder_selected

def load_images_from_folder(folder):
    images = []
    for filename in sorted(os.listdir(folder)):
        if filename.endswith(".tif"):
            img = Image.open(os.path.join(folder, filename))
            images.append(np.array(img))
    return images

def convert_pixels_to_mm(images, pixel_size_mm,treshold):
    converted_images = []
    for img in images:
        coords = np.argwhere(img >= treshold)  
        if coords.size > 0:
            coords_mm = coords * pixel_size_mm
            converted_images.append(coords_mm)
    return converted_images

def filter_noise_with_dbscan(coords, eps, min_samples):
    if len(coords) == 0:
        return np.array([])  
    
    db = DBSCAN(eps=eps, min_samples=min_samples).fit(coords)
    labels = db.labels_
    
    filtered_coords = coords[labels != -1]
    return filtered_coords

def plot_spatio_temporal_3d(images, acquisition_rate_hz, pixel_size_mm, eps, min_samples, use_dbscan):
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    time_interval_ms = 1000 / acquisition_rate_hz
    
    x_coords_mm = []
    y_coords_mm = []
    z_coords_ms = []
    
    for i, img_coords in enumerate(images):
        time_ms = i * time_interval_ms
        if img_coords.size > 0:
            if use_dbscan:
                filtered_coords = filter_noise_with_dbscan(img_coords, eps, min_samples)
            else:
                filtered_coords = img_coords
            if len(filtered_coords) > 0:
                x_coords_mm.extend(filtered_coords[:, 1])  # Convert columns to mm
                y_coords_mm.extend(filtered_coords[:, 0])  # Convert rows to mm
                z_coords_ms.extend([time_ms] * len(filtered_coords))
    
    ax.scatter(x_coords_mm, y_coords_mm, z_coords_ms, c='b')  # Use a single color (blue) for all points

    ax.set_xlabel('X (mm)')
    ax.set_ylabel('Y (mm)')
    ax.set_zlabel('Time (ms)')
    ax.set_title('Spatio-temporal 3D plot of white pixels')
    plt.show()

def main():
    pixel_size_mm = 4 / 408  # 4 mm = 408 pixels
    acquisition_rate_hz = 50000  # 50,000 images per second
    eps = 0.01  #0.01 Mini
    min_samples = 5
    treshold=70

    folder = select_folder()
    images = load_images_from_folder(folder)
    images_mm = convert_pixels_to_mm(images, pixel_size_mm,treshold)

    root = Tk()
    root.withdraw()
    use_dbscan = simpledialog.askstring("Input", "Do you want to use DBSCAN for noise filtering? (yes/no)").lower() == 'yes'
    root.destroy()

    plot_spatio_temporal_3d(images_mm, acquisition_rate_hz, pixel_size_mm, eps, min_samples, use_dbscan)

if __name__ == "__main__":
    main()
