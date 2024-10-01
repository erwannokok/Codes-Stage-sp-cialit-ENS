from tkinter import filedialog
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from sklearn.cluster import DBSCAN
from st_dbscan import ST_DBSCAN
import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np

taille_pixel=0.06

def fermer_figures():
    plt.close('all')



def ouvrir_fichier():
    global data
    chemin_fichier = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if chemin_fichier:
        data = pd.read_csv(chemin_fichier, header=None, names=['x', 'y', 'p', 't'],skiprows=1)
        data['t'] = data['t'] / 1000
        messagebox.showinfo("Information", f"Le fichier {chemin_fichier} a bien été ouvert.")

# Fonction pour filtrer les données selon les intervalles de temps et la polarité
def filtrer_donnees(temps_min=None, temps_max=None, x_min=None, x_max=None, y_min=None, y_max=None):
    global data
    if temps_min is None:
        temps_min = 0
    if temps_max is None:
        temps_max = 1000000000000
    
    
    donnees_filtrees = data[(data['p'] == 1) & 
                            (data['t'] >= temps_min) & 
                            (data['t'] <= temps_max)]
    if x_min is not None and x_max is not None:
        donnees_filtrees = donnees_filtrees[(data['x'] >= x_min) & (data['x'] <= x_max)]
    if y_min is not None and y_max is not None:
        donnees_filtrees = donnees_filtrees[(data['y'] >= y_min) & (data['y'] <= y_max)]
    return donnees_filtrees

def effectuer_clustering(donnees_filtrees, eps1, eps2, minPts, algo):
    
    if algo == 'DBSCAN':
        dbscan = DBSCAN(eps=eps1, min_samples=minPts)
        dbscan.fit(donnees_filtrees[['x', 'y','t']].values)
        clusters = dbscan.labels_
        
    elif algo == 'ST_DBSCAN':
        st_dbscan = ST_DBSCAN(eps1, eps2, min_samples=minPts)
        st_dbscan.fit(donnees_filtrees[['t', 'x', 'y']].values)

        clusters = st_dbscan.labels
    
    donnees_filtrees['cluster'] = clusters
    donnees_clusterisees = donnees_filtrees[clusters != -1]
    return donnees_clusterisees

    

def attribuer_couleurs_clusters(donnees_clusterisees):
    clusters_uniques = donnees_clusterisees['cluster'].unique()
    couleurs = plt.cm.viridis(np.linspace(0, 1, len(clusters_uniques)))
    dic_couleurs_clusters = {cluster: couleur for cluster, couleur in zip(clusters_uniques, couleurs)}
    return dic_couleurs_clusters

def afficher_points_un_a_un_3d(donnees, dic_couleurs_clusters, utiliser_couleurs):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    
    donnees_triees = donnees.sort_values(by='t')
    
    for index, point in donnees_triees.iterrows():
        couleur = dic_couleurs_clusters[point['cluster']] if utiliser_couleurs else 'b'
        ax.scatter(point['x'] * taille_pixel, point['y'] * taille_pixel, point['t'], color=couleur, marker='o')
        plt.draw()
        plt.pause(0.000000001)
        
    ax.set_xlabel('X (mm)')
    ax.set_ylabel('Y (mm)')
    ax.set_zlabel('Temps (ms) ')
    plt.show()
    plt.close()


def afficher_points_un_a_un(donnees, etiquette_x, etiquette_y, dic_couleurs_clusters, utiliser_couleurs):
    plt.figure()
    
    donnees_triees = donnees.sort_values(by='t')

    for index, point in donnees_triees.iterrows():
        couleur = dic_couleurs_clusters[point['cluster']] if utiliser_couleurs else 'b'
        plt.scatter(point['t'], point['y'] * taille_pixel, color=couleur, marker='o')
        plt.draw()
        plt.pause(0.0001)
    
    plt.xlabel(etiquette_x)
    plt.ylabel('Y (mm)')
    plt.show()
    plt.close()


def tracer_y_en_fonction_du_temps_pour_x(donnees, valeur_x, dic_couleurs_clusters, utiliser_couleurs, point_par_point=False):
    sous_ensemble = donnees[donnees['x'] == valeur_x]
    
    if point_par_point:
        afficher_points_un_a_un(sous_ensemble, 'Temps', 'Y (mm)', dic_couleurs_clusters, utiliser_couleurs)
    else:
        plt.figure()
        couleurs = [dic_couleurs_clusters[cluster] if utiliser_couleurs else 'b' for cluster in sous_ensemble['cluster']]
        plt.scatter(sous_ensemble['t'], sous_ensemble['y'] * taille_pixel, c=couleurs, marker='o')

        if not sous_ensemble.empty:
            coef = np.polyfit(sous_ensemble['t'], sous_ensemble['y'] * taille_pixel, 1)
            poly1d_fn = np.poly1d(coef)
            plt.plot(sous_ensemble['t'], poly1d_fn(sous_ensemble['t']), color='red', linestyle='--', linewidth=2)
            slope = coef[0]
            
            plt.annotate(f"Pente: {slope:.2f}", xy=(0.05, 0.95), xycoords='axes fraction', fontsize=12, color='red', verticalalignment='top')
        
        plt.xlabel('Temps (ms) ')
        plt.ylabel('Y (mm)')
        plt.title(f'Y en fonction du Temps pour X = {valeur_x * taille_pixel} mm')
        plt.show()



def tracer_x_en_fonction_du_temps_pour_y(donnees, valeur_y, dic_couleurs_clusters, utiliser_couleurs, point_par_point=False):
    sous_ensemble = donnees[donnees['y'] == valeur_y]
    
    if point_par_point:
        afficher_points_un_a_un(sous_ensemble, 'Temps', 'X (mm)', dic_couleurs_clusters, utiliser_couleurs)
    else:
        plt.figure()
        couleurs = [dic_couleurs_clusters[cluster] if utiliser_couleurs else 'b' for cluster in sous_ensemble['cluster']]
        plt.scatter(sous_ensemble['t'], sous_ensemble['x'] * taille_pixel, c=couleurs, marker='o')

        if not sous_ensemble.empty:
            coef = np.polyfit(sous_ensemble['t'], sous_ensemble['x'] * taille_pixel, 1)
            poly1d_fn = np.poly1d(coef)
            plt.plot(sous_ensemble['t'], poly1d_fn(sous_ensemble['t']), color='red', linestyle='--', linewidth=2)
            slope = coef[0]
            
            plt.annotate(f"Pente: {slope:.2f}", xy=(0.05, 0.95), xycoords='axes fraction', fontsize=12, color='red', verticalalignment='top')
        
        plt.xlabel('Temps')
        plt.ylabel('X (mm)')
        plt.title(f'X en fonction du Temps pour Y = {valeur_y * taille_pixel} mm')
        plt.show()

def executer_interface():
    def sur_changement_mode(*args):
        mode = var_mode.get()
        if mode == '3' or mode == '4':
            sous_mode_normal.config(state='normal')
            sous_mode_point.config(state='normal')
        else:
            sous_mode_normal.config(state='disabled')
            sous_mode_point.config(state='disabled')

        if mode == '3':
            entree_y.config(state='normal')
            entree_x.config(state='disabled')
        elif mode == '4':
            entree_x.config(state='normal')
            entree_y.config(state='disabled')
        else:
            entree_x.config(state='disabled')
            entree_y.config(state='disabled')
        
    def sur_changement_algo(*args):
        if var_algo.get() == 'DBSCAN':
            entree_epsilon2.config(state='disabled')
        else:
            entree_epsilon2.config(state='normal')

    def convertir_mm_en_pixels(valeur_mm):
        return valeur_mm / taille_pixel

    def sur_validation():
        try:
            if var_temps.get() == '1':
                temps_min = float(entree_temps_min.get())
                temps_max = float(entree_temps_max.get())
                if temps_min is None or temps_max is None:  
                    raise ValueError("Veuillez entrer des valeurs pour l'intervalle de temps.")  
            else:
                temps_min, temps_max = None, None

            eps1 = float(entree_epsilon1.get())
            eps2 = float(entree_epsilon2.get()) if var_algo.get() == 'ST_DBSCAN' else None
            minPts = int(entree_minPts.get())   
            algo = var_algo.get()
            
            if algo == 'DBSCAN':
                entree_epsilon2.config(state='disabled')
            else:
                entree_epsilon2.config(state='normal')

            

            if var_roi.get() == '1':
                x_min = float(entree_x_min.get())
                x_max = float(entree_x_max.get())
                y_min = float(entree_y_min.get())
                y_max = float(entree_y_max.get())
            
                x_min_pixels = convertir_mm_en_pixels(x_min)
                x_max_pixels = convertir_mm_en_pixels(x_max)
                y_min_pixels = convertir_mm_en_pixels(y_min)
                y_max_pixels = convertir_mm_en_pixels(y_max)
            else:
                x_min_pixels = x_max_pixels = y_min_pixels = y_max_pixels = None
            donnees_filtrees = filtrer_donnees(temps_min, temps_max, x_min_pixels, x_max_pixels, y_min_pixels, y_max_pixels)
            donnees_clusterisees = effectuer_clustering(donnees_filtrees, eps1, eps2, minPts, algo)
            dic_couleurs_clusters = attribuer_couleurs_clusters(donnees_clusterisees)
            utiliser_couleurs = var_couleur.get() == '1'

            mode = var_mode.get()
            if mode == '1':
                fig = plt.figure()
                ax = fig.add_subplot(111, projection='3d')
                couleurs = [dic_couleurs_clusters[cluster] if utiliser_couleurs else 'b' for cluster in donnees_clusterisees['cluster']]
                scatter = ax.scatter(donnees_clusterisees['x'] * taille_pixel, donnees_clusterisees['y'] * taille_pixel, donnees_clusterisees['t'], c=couleurs, marker='o')
                ax.set_xlabel('X (mm)')
                ax.set_ylabel('Y (mm)')
                ax.set_zlabel('Temps (ms) ')
                plt.show()
                label_nombre_points.config(text=f"Nombre de points affichés: {len(donnees_clusterisees)}")
                nombre_clusters = len(donnees_clusterisees['cluster'].unique())
                label_nombre_clusters.config(text=f"Nombre de clusters trouvés: {nombre_clusters}")

            elif mode == '2':
                afficher_points_un_a_un_3d(donnees_clusterisees, dic_couleurs_clusters, utiliser_couleurs)
            elif mode == '3':
                try:
                    valeur_y = float(entree_y.get())
                    sous_mode = var_sous_mode.get()
                    if sous_mode == '1':
                        tracer_x_en_fonction_du_temps_pour_y(donnees_clusterisees, valeur_y, dic_couleurs_clusters, utiliser_couleurs, point_par_point=False)
                    elif sous_mode == '2':
                        tracer_x_en_fonction_du_temps_pour_y(donnees_clusterisees, valeur_y, dic_couleurs_clusters, utiliser_couleurs, point_par_point=True)
                except ValueError:
                    messagebox.showerror("Erreur", "Veuillez entrer une valeur numérique pour Y.")
            elif mode == '4':
                try:
                    valeur_x = float(entree_x.get())
                    sous_mode = var_sous_mode.get()
                    if sous_mode == '1':
                        tracer_y_en_fonction_du_temps_pour_x(donnees_clusterisees, valeur_x, dic_couleurs_clusters, utiliser_couleurs, point_par_point=False)
                    elif sous_mode == '2':
                        tracer_y_en_fonction_du_temps_pour_x(donnees_clusterisees, valeur_x, dic_couleurs_clusters, utiliser_couleurs, point_par_point=True)
                except ValueError:
                    messagebox.showerror("Erreur", "Veuillez entrer une valeur numérique pour X.")
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer des valeurs numériques pour l'intervalle de temps, epsilon et minPts.")

    
    def on_roi_check():
        if var_roi.get() == '1':
            frame_roi.grid()
        else:
            frame_roi.grid_remove()

    def on_temps_check():
        if var_temps.get() == '1':
            frame_temps.grid()
        else:
            frame_temps.grid_remove()

    root = tk.Tk()
    root.title("Interface de Visualisation de Données")

    ttk.Button(root, text="Ouvrir", command=ouvrir_fichier).grid(column=0, row=0, columnspan=2, padx=10, pady=10)

    ttk.Label(root, text="Choisissez le mode d'affichage:").grid(column=0, row=1, padx=10, pady=10, sticky='w')
    
    var_mode = tk.StringVar(value='1')
    var_mode.trace('w', lambda *args: sur_changement_mode())
    modes = [("3D Normal", '1'), ("3D Point par Point", '2'), ("2D X en fonction du Temps pour Y", '3'), ("2D Y en fonction du Temps pour X", '4')]
    for text, mode in modes:
        ttk.Radiobutton(root, text=text, variable=var_mode, value=mode).grid(column=0, row=int(mode)+1, padx=10, pady=5, sticky='w')

    var_temps = tk.StringVar(value='0')
    ttk.Checkbutton(root, text="Choisir Temps", variable=var_temps).grid(column=0, row=6, columnspan=2, padx=10, pady=5, sticky='w')

    frame_temps = ttk.Frame(root)
    frame_temps.grid(column=0, row=7, columnspan=2, padx=10, pady=5, sticky='w')
    frame_temps.grid_remove()

    ttk.Label(frame_temps, text="Temps Min:").grid(column=0, row=0, padx=10, pady=5, sticky='w')
    entree_temps_min = ttk.Entry(frame_temps)
    entree_temps_min.grid(column=1, row=0, padx=10, pady=5)

    ttk.Label(frame_temps, text="Temps Max:").grid(column=0, row=1, padx=10, pady=5, sticky='w')
    entree_temps_max = ttk.Entry(frame_temps)
    entree_temps_max.grid(column=1, row=1, padx=10, pady=5)

    var_temps.trace('w', lambda *args: on_temps_check())

    
    var_roi = tk.StringVar(value='0')
    ttk.Checkbutton(root, text="Utiliser une ROI", variable=var_roi).grid(column=0, row=8, columnspan=2, padx=10, pady=5, sticky='w')

    frame_roi = ttk.Frame(root)
    frame_roi.grid(column=0, row=9, columnspan=2, padx=10, pady=5, sticky='w')
    frame_roi.grid_remove()

    ttk.Label(frame_roi, text="X Min:").grid(column=0, row=0, padx=10, pady=5, sticky='w')
    entree_x_min = ttk.Entry(frame_roi)
    entree_x_min.grid(column=1, row=0, padx=10, pady=5)

    ttk.Label(frame_roi, text="X Max:").grid(column=0, row=1, padx=10, pady=5, sticky='w')
    entree_x_max = ttk.Entry(frame_roi)
    entree_x_max.grid(column=1, row=1, padx=10, pady=5)

    ttk.Label(frame_roi, text="Y Min:").grid(column=0, row=2, padx=10, pady=5, sticky='w')
    entree_y_min = ttk.Entry(frame_roi)
    entree_y_min.grid(column=1, row=2, padx=10, pady=5)

    ttk.Label(frame_roi, text="Y Max:").grid(column=0, row=3, padx=10, pady=5, sticky='w')
    entree_y_max = ttk.Entry(frame_roi)
    entree_y_max.grid(column=1, row=3, padx=10, pady=5)

    var_roi.trace('w', lambda *args: on_roi_check())

    frame_eps_minPts = ttk.Frame(root)
    frame_eps_minPts.grid(column=0, row=10, columnspan=2, padx=10, pady=5, sticky='w')

    # Widgets pour epsilon et minPts
    ttk.Label(frame_eps_minPts, text="Epsilon1:").grid(column=0, row=0, padx=10, pady=5, sticky='w')
    entree_epsilon1 = ttk.Entry(frame_eps_minPts)
    entree_epsilon1.grid(column=1, row=0, padx=10, pady=5)

    ttk.Label(frame_eps_minPts, text="Epsilon2:").grid(column=0, row=1, padx=10, pady=5, sticky='w')
    entree_epsilon2 = ttk.Entry(frame_eps_minPts)
    entree_epsilon2.grid(column=1, row=1, padx=10, pady=5)

    ttk.Label(frame_eps_minPts, text="minPts:").grid(column=0, row=2, padx=10, pady=5, sticky='w')
    entree_minPts = ttk.Entry(frame_eps_minPts)
    entree_minPts.grid(column=1, row=2, padx=10, pady=5)

    ttk.Label(root, text="Choisissez l'algorithme:").grid(column=0, row=19, padx=10, pady=10, sticky='w')

    var_algo = tk.StringVar(value='DBSCAN')
    algo_combobox = ttk.Combobox(root, textvariable=var_algo, values=['DBSCAN', 'ST_DBSCAN'])
    algo_combobox.grid(column=1, row=19, padx=10, pady=10, sticky='w')
    # Correction de la récupération des valeurs de la combobox

    if var_algo.get() == 'DBSCAN':
        entree_epsilon2.config(state='disabled')


    var_algo.trace('w', lambda *args: sur_changement_algo())
    


# Option pour la couleur par cluster
    ttk.Label(root, text="Couleur par cluster:").grid(column=0, row=12, padx=10, pady=10, sticky='w')
    var_couleur = tk.StringVar(value='0')
    ttk.Checkbutton(root, variable=var_couleur).grid(column=1, row=12, sticky='w')

    ttk.Button(root, text="Valider", command=sur_validation).grid(column=0, row=13, columnspan=2, padx=10, pady=10)
    

    ttk.Label(root, text="Y:").grid(column=0, row=15, padx=10, pady=10, sticky='w')
    entree_y = ttk.Entry(root)
    entree_y.grid(column=1, row=15, padx=10, pady=10, sticky='w')
    entree_y.config(state='disabled')

    ttk.Label(root, text="X:").grid(column=0, row=16, padx=10, pady=10, sticky='w')
    entree_x = ttk.Entry(root)
    entree_x.grid(column=1, row=16, padx=10, pady=10, sticky='w')
    entree_x.config(state='disabled')

    var_sous_mode = tk.StringVar(value='1')
    sous_mode_normal = ttk.Radiobutton(root, text="Normal", variable=var_sous_mode, value='1')
    sous_mode_point = ttk.Radiobutton(root, text="Point par Point", variable=var_sous_mode, value='2')
    sous_mode_normal.grid(column=0, row=17, padx=10, pady=5, sticky='w')
    sous_mode_point.grid(column=1, row=17, padx=10, pady=5, sticky='w')
    sous_mode_normal.config(state='disabled')
    sous_mode_point.config(state='disabled')

    
    global label_nombre_points
    label_nombre_points = ttk.Label(root, text="Nombre de points affichés: 0")
    label_nombre_points.grid(column=0, row=20, columnspan=2, padx=10, pady=10)
    label_nombre_clusters = ttk.Label(root, text="Nombre de clusters trouvés: 0")
    label_nombre_clusters.grid(column=0, row=21, columnspan=2, padx=10, pady=10)
    root.protocol("WM_DELETE_WINDOW", lambda: (fermer_figures(), root.destroy()))
    root.mainloop()


if __name__ == "__main__":
    executer_interface()

