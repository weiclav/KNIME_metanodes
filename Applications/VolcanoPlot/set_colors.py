import pandas as pd
import numpy as np

def set_color(dff, derived_virtual_selected_rows, col_name_logFC, col_name_p_value, effects, effects_p, colorblind):

    significant_color = 'rgba(255,221,0, 0.8)'
    sign_up_color = 'rgba(255,0,0, 0.8)'
    sign_down_color = 'rgba(0,255,0, 0.8)'
    not_sign_color = 'rgba(0,170,255, 0.8)'

    if colorblind:
        significant_color ='rgba(220,172,0, 0.6)'
        sign_up_color = 'rgba(152,0,0, 0.5)'
        sign_down_color = 'rgba(0,52,131,0.5)'
        not_sign_color = 'rgba(30,136,126,0.5)'


    category_color = []

    for index, row in dff.iterrows():

        if row[col_name_logFC] <= effects[1] and row[col_name_logFC] >= effects[0] and -np.log10(
                row[col_name_p_value]) > effects_p:
            category_color.append(significant_color)

        elif row[col_name_logFC] > effects[1] and -np.log10(row[col_name_p_value]) > effects_p:
            category_color.append(sign_up_color)

        elif row[col_name_logFC] < effects[0] and -np.log10(row[col_name_p_value]) > effects_p:
            category_color.append(sign_down_color)

        else:
            category_color.append(not_sign_color)

    colors = [category_color[i] if i in derived_virtual_selected_rows else category_color[i]
              for i in range(len(dff))]

    return colors
