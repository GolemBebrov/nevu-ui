class Annotations:
    #=== size annotations ===
    any_number = float | int
    dest_like = tuple[any_number, any_number] | list[any_number]
    rect_like = tuple[any_number, any_number, any_number, any_number] | list[any_number]
    
    #=== color annotations ===
    rgb_color = tuple[int, int, int]
    rgba_color = tuple[int, int, int, int]
    rgb_like_color = rgb_color | rgba_color
    hsl_color = tuple[float, float, float]
    hex_color = str
    any_color = rgb_like_color | hsl_color | hex_color