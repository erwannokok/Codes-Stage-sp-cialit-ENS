import numpy as np
from PIL import Image
import os
import sys
from tkinter import Tk, filedialog, Button, Checkbutton, IntVar, Label, Entry

def tiff_to_grayscale_array(file_path):
    with Image.open(file_path) as img:
        arrimg = np.array(img)
        arrimgnorm = arrimg // (4095 / 255)
    return arrimgnorm.astype(np.uint8)

def save_image(image_array, output_path):
    image = Image.fromarray(image_array.astype(np.uint8))
    image.save(output_path)

def calculate_gradient_magnitude(image):
    grad_x = np.gradient(image.astype(float), axis=1)
    grad_y = np.gradient(image.astype(float), axis=0)
    gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
    return gradient_magnitude

def binarize_image(image_array, threshold):
    return (image_array > threshold).astype(np.uint8) * 255

def process_images():
    # Sélection du dossier contenant les images TIFF
    dossier = filedialog.askdirectory(title="Sélectionnez un dossier contenant les images TIFF")
    if not dossier:
        sys.exit("Aucun dossier sélectionné. Le programme va maintenant se terminer.")
    
    # Sélection du dossier de sortie pour les images binarisées
    output_dossier = filedialog.askdirectory(title="Sélectionnez un dossier de sortie pour les images binarisées")
    if not output_dossier:
        sys.exit("Aucun dossier de sortie sélectionné. Le programme va maintenant se terminer.")
    
    # Lire le seuil de binarisation
    if not no_binarization.get():
        try:
            threshold = int(threshold_entry.get())
        except ValueError:
            sys.exit("Veuillez entrer un seuil valide (0-255). Le programme va maintenant se terminer.")
    
    # Liste pour stocker les images et les gradients spatiaux
    original_images = []
    processed_images = []
    image_names = []

    # Parcourir les images dans le dossier
    for image_name in os.listdir(dossier):
        if image_name.endswith(".tif"):
            file_path = os.path.join(dossier, image_name)
            
            # Convertir en niveaux de gris
            grey_img = tiff_to_grayscale_array(file_path)
            
            if binarize_only.get():
                bin_img = binarize_image(grey_img, threshold)
                # Sauvegarder l'image binarisée uniquement
                output_path = os.path.join(output_dossier, f"binarize_only_{image_name}")
                save_image(bin_img, output_path)
                continue  
            
            if binarize_before_gradient.get() and not no_binarization.get():
                grey_img = binarize_image(grey_img, threshold)
                # Sauvegarder l'image binarisée avant gradient
                output_path = os.path.join(output_dossier, f"binarized_before_gradient_{image_name}")
                save_image(grey_img, output_path)
            
            original_images.append(grey_img)
            image_names.append(image_name)
            
            if calculate_spatial_gradient.get():
                # Calculer la norme des gradients spatiaux
                gradient_magnitude = calculate_gradient_magnitude(grey_img)
                processed_images.append(gradient_magnitude)
                
                if binarize_before_gradient.get() :
                        output_path = os.path.join(output_dossier, f"binarized_and_gradient_spatial{image_name}")
                        save_image(gradient_magnitude, output_path)
                
                
                if binarize_after_gradient.get() and not calculate_temporal_gradient.get():
                    gradient_magnitude_binarized = binarize_image(gradient_magnitude, threshold)
                    # Sauvegarder l'image de gradient spatial binarisée
                    output_path = os.path.join(output_dossier, f"gradient_spatial_binarized_{image_name}")
                    save_image(gradient_magnitude_binarized, output_path)

                

                if not binarize_before_gradient.get() and not binarize_after_gradient.get():
                    
                    output_path = os.path.join(output_dossier, f"gradient_spatial_{image_name}")
                    save_image(gradient_magnitude, output_path)
            else:
                processed_images.append(grey_img)

    # Calculer le gradient temporel si demandé
    if calculate_temporal_gradient.get() and not binarize_only.get():
        for i in range(1, len(processed_images)):
            # Calculer la différence entre deux images successives
            gradient_temp = np.abs(processed_images[i] - processed_images[i-1])
            
            if binarize_after_gradient.get() :
            
                    gradient_temp_binarized = binarize_image(gradient_temp, threshold)
                    if calculate_spatial_gradient.get():
                        output_path = os.path.join(output_dossier, f"gradient_spatial_temporel_binarized_{image_names[i]}")
                    else :
                        output_path = os.path.join(output_dossier, f"gradient_temporel_binarized_{image_names[i]}")
                    
                    save_image(gradient_temp_binarized, output_path)

            if binarize_before_gradient.get() :
                if calculate_spatial_gradient.get():
                
                    output_path = os.path.join(output_dossier, f"binarized_gradient_spatial_temporel{image_names[i]}")
                else:
                    output_path = os.path.join(output_dossier, f"binarized_gradient_temporel{image_names[i]}")
                save_image(gradient_temp, output_path)

            else :
                output_path = os.path.join(output_dossier, f"gradient_spatial_temporel{image_names[i]}")
                save_image(gradient_temp, output_path)


    print("Traitement terminé.")

# Créer la fenêtre principale
root = Tk()
root.title("Traitement d'images TIFF")

# Variables pour les options
calculate_spatial_gradient = IntVar()
calculate_temporal_gradient = IntVar()
binarize_before_gradient = IntVar()
binarize_after_gradient = IntVar()
binarize_only = IntVar()
no_binarization = IntVar()

# Interface utilisateur
Label(root, text="Options de traitement :").grid(row=0, column=0, columnspan=2)

Checkbutton(root, text="Calculer les gradients spatiaux", variable=calculate_spatial_gradient).grid(row=1, column=0, sticky='w')
Checkbutton(root, text="Calculer les gradients temporels", variable=calculate_temporal_gradient).grid(row=2, column=0, sticky='w')

Label(root, text="Binarisation :").grid(row=3, column=0, sticky='w')

Checkbutton(root, text="Binariser uniquement", variable=binarize_only).grid(row=4, column=0, sticky='w')
Checkbutton(root, text="Binariser avant calcul des gradients", variable=binarize_before_gradient).grid(row=5, column=0, sticky='w')
Checkbutton(root, text="Binariser après calcul des gradients", variable=binarize_after_gradient).grid(row=6, column=0, sticky='w')
Checkbutton(root, text="Pas de binarisation", variable=no_binarization).grid(row=7, column=0, sticky='w')

Label(root, text="Seuil de binarisation (0-255) :").grid(row=8, column=0, sticky='w')
threshold_entry = Entry(root)
threshold_entry.grid(row=8, column=1, sticky='w')

Button(root, text="Démarrer le traitement", command=process_images).grid(row=9, column=0, columnspan=2, pady=10)

# Lancer la boucle principale
root.mainloop()
