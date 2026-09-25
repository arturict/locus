#!/usr/bin/env python3
"""Generate the Locus UI icons listed in tools/images-sourced.txt.

Sources: Material Symbols Outlined (Apache 2.0), Font Awesome Free (icons
CC BY 4.0) and icons drawn for Locus in drawn.py (EUPL 1.2). Glyphs in drawn
icons are outlines of Noto Sans / Noto Serif / Noto Sans Math (SIL OFL 1.1)
converted to paths, so no SVG refers to a font.

Usage (from the repository root):
    python3 -m venv --system-site-packages /tmp/icons-venv
    /tmp/icons-venv/bin/pip install fonttools
    /tmp/icons-venv/bin/python tools/icons/build_icons.py

Needs npm (downloads the two icon packages into ~/.cache/locus-icons), the Noto
fonts in /usr/share/fonts/truetype/noto, Pillow and Playwright with Chrome for
the PNG and GIF variants. Writes the icons in place and the provenance table
tools/icons/sourced-icons.tsv.
"""
import io
import math
import re
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
import drawn  # noqa: E402
import iconlib as L  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
C = "source/shared/common/src/main/resources/org/geogebra/common/icons/"
MD = C + "svg/web/matDesignIcons/"
KB = C + "svg/web/keyboard/"
PNG = C + "png/web/"
SPINNER = "source/web/web-common/src/main/resources/org/geogebra/web/resources/images/spinner.gif"

W, N, T = L.WHITE, L.NEUTRAL, L.TEXT


def ms(name, color=N, **kw):
    return dict(kind="ms", name=name, color=color, **kw)


def fa(name, color=N, **kw):
    return dict(kind="fa", name=name, color=color, **kw)


def dr(name, color=N, **kw):
    return dict(kind="drawn", name=name, color=color, **kw)


def raw(name, **kw):
    return dict(kind="raw", name=name, **kw)


def kb(name, **kw):
    return dr(name, T, **kw)


SPEC = {
    # ---------------------------------------------------------------- algebra view
    MD + "av/baseline-clear-24px.svg": ms("close"),
    MD + "av/baseline-timeline-24px.svg": ms("timeline"),
    MD + "av/engineering_notation_white.svg": dr("engineering", W),
    MD + "av/equal_sign.svg": dr("equal"),
    MD + "av/equal_sign_white.svg": dr("equal", W),
    MD + "av/fraction_white.svg": dr("fraction_digits", W),
    MD + "av/ic_pause_circle_outline_black_24px.svg": ms("pause_circle"),
    MD + "av/minus.svg": ms("remove"),
    MD + "av/mode_symbolic_white.svg": dr("approx", W),
    MD + "av/plusMenu/add.svg": ms("add"),
    MD + "av/plusMenu/ic_format_quote_black_24px.svg": ms("format_quote"),
    MD + "av/plusMenu/ic_image_black_24px.svg": ms("image"),
    MD + "av/speed_down_black.svg": ms("keyboard_double_arrow_left"),
    MD + "av/speed_up_black.svg": ms("keyboard_double_arrow_right"),
    MD + "av/statistics.svg": ms("query_stats"),
    MD + "av/wrong_input.svg": ms("warning"),
    # ---------------------------------------------------------------- main menu
    MD + "burgerMenu/assignment-24px.svg": ms("assignment"),
    MD + "burgerMenu/book-logo.svg": ms("menu_book"),
    MD + "burgerMenu/code_white_24px.svg": ms("code", W),
    MD + "burgerMenu/exit_to_app-24px.svg": ms("login"),
    MD + "burgerMenu/geogebra_color.svg": raw("logo_color"),
    MD + "burgerMenu/geogebra.svg": dr("logo"),
    MD + "burgerMenu/help-24px.svg": ms("help"),
    MD + "burgerMenu/hourglass_empty-24px.svg": ms("hourglass_empty"),
    MD + "burgerMenu/ic_bug_report_black_24px.svg": ms("bug_report"),
    MD + "burgerMenu/ic_collections_black_24px.svg": ms("photo_library"),
    MD + "burgerMenu/ic_content_copy_black_24px.svg": ms("content_copy"),
    MD + "burgerMenu/ic_content_paste_black_24px.svg": ms("content_paste"),
    MD + "burgerMenu/ic_file_download_black_24px.svg": ms("download"),
    MD + "burgerMenu/ic_file_download_white_24px.svg": ms("download", W),
    MD + "burgerMenu/ic_info_outline_black_24px.svg": ms("info"),
    MD + "burgerMenu/ic_insert_drive_file_black_24px.svg": ms("draft"),
    MD + "burgerMenu/ic_mode_edit_black_24px.svg": ms("edit"),
    MD + "burgerMenu/ic_person_black_24px.svg": ms("person"),
    MD + "burgerMenu/ic_print_black_24px.svg": ms("print"),
    MD + "burgerMenu/ic_print_white_24px.svg": ms("print", W),
    MD + "burgerMenu/ic_redo_black_24px.svg": ms("redo"),
    MD + "burgerMenu/ic_save_black_24px.svg": ms("save"),
    MD + "burgerMenu/ic_save_online_black_24px.svg": ms("cloud_upload"),
    MD + "burgerMenu/ic_search_black_24px.svg": ms("search"),
    MD + "burgerMenu/ic_select_all_black_24px.svg": ms("select_all"),
    MD + "burgerMenu/ic_share_black_24px.svg": ms("share"),
    MD + "burgerMenu/ic_undo_black_24px.svg": ms("undo"),
    MD + "burgerMenu/info-24px.svg": ms("info"),
    MD + "burgerMenu/logout.svg": ms("logout"),
    # partner logo slot: Locus has no partner branding, a neutral school icon fills it
    MD + "burgerMenu/mebis-logo.png": ms("school", png=(48, 48)),
    MD + "burgerMenu/menu_whiteBorder.svg": ms("menu"),
    MD + "burgerMenu/multiple-worksheets.svg": ms("library_books"),
    MD + "burgerMenu/privacy_tip.svg": ms("privacy_tip"),
    MD + "burgerMenu/report.svg": ms("report"),
    MD + "burgerMenu/school-24px.svg": ms("school"),
    MD + "burgerMenu/scientific.svg": ms("calculate"),
    MD + "burgerMenu/signin_black.svg": ms("login"),
    MD + "burgerMenu/signout_black.svg": ms("logout"),
    # ---------------------------------------------------------------- context menu
    MD + "contextMenu/add_column_left.svg": ms("add_column_left"),
    MD + "contextMenu/add_column_right.svg": ms("add_column_right"),
    MD + "contextMenu/add_row_above.svg": ms("add_row_above"),
    MD + "contextMenu/add_row_below.svg": ms("add_row_below"),
    MD + "contextMenu/angle_black.svg": dr("angle"),
    MD + "contextMenu/arrow_drop_left_black.svg": ms("arrow_left"),
    MD + "contextMenu/arrow_drop_right_black.svg": ms("arrow_right"),
    MD + "contextMenu/boxplot.svg": dr("boxplot"),
    MD + "contextMenu/chart_bar.svg": ms("bar_chart"),
    MD + "contextMenu/chart_line.svg": ms("show_chart"),
    MD + "contextMenu/chart_pie.svg": ms("pie_chart"),
    MD + "contextMenu/check_box_checked.svg": ms("check_box-fill"),
    MD + "contextMenu/check_box_unchecked.svg": ms("check_box_outline_blank"),
    MD + "contextMenu/control_point_duplicate.svg": ms("control_point_duplicate"),
    MD + "contextMenu/delete_outline.svg": ms("delete"),
    MD + "contextMenu/duplicate_black.svg": ms("control_point_duplicate"),
    MD + "contextMenu/format_list_bulleted-24px.svg": ms("format_list_bulleted"),
    MD + "contextMenu/format_list_numbered-24px.svg": ms("format_list_numbered"),
    MD + "contextMenu/format_subscript.svg": ms("subscript"),
    MD + "contextMenu/format_superscript.svg": ms("superscript"),
    MD + "contextMenu/functions.svg": ms("functions"),
    MD + "contextMenu/histogram.svg": dr("histogram"),
    MD + "contextMenu/ic_check_black_24px.svg": ms("check"),
    MD + "contextMenu/ic_check_white_24px.svg": ms("check", W),
    MD + "contextMenu/ic_content_cut_black_24px.svg": ms("content_cut"),
    MD + "contextMenu/ic_delete_black_24px.svg": ms("delete"),
    MD + "contextMenu/ic_expand_less_black_24px.svg": ms("keyboard_arrow_up"),
    MD + "contextMenu/ic_expand_more_black_24px.svg": ms("keyboard_arrow_down"),
    MD + "contextMenu/ic_home_black_24px.svg": ms("home"),
    MD + "contextMenu/ic_label_outline_black_24px.svg": ms("label"),
    MD + "contextMenu/ic_lock_open_black_24px.svg": ms("lock_open"),
    MD + "contextMenu/ic_lock_outline_black_24px.svg": ms("lock"),
    MD + "contextMenu/ic_more_vert_black_24px.svg": ms("more_vert"),
    MD + "contextMenu/ic_play_circle_outline_black_24px.svg": ms("play_circle"),
    MD + "contextMenu/insert_chart.svg": ms("insert_chart"),
    MD + "contextMenu/pin_black.svg": ms("keep"),
    MD + "contextMenu/plane_black.svg": dr("plane"),
    MD + "contextMenu/record_to_spreadsheet_black.svg": dr("record_to_table"),
    MD + "contextMenu/rename_black.svg": ms("edit_note"),
    MD + "contextMenu/show_all_objects_black.svg": ms("fit_screen"),
    MD + "contextMenu/table_heading_column.svg": dr("heading_column"),
    MD + "contextMenu/table_heading_row.svg": dr("heading_row"),
    C + "png/matDesignIcons/contextMenu/trace_black.png": raw("trace", png=(24, 24)),
    # ---------------------------------------------------------------- data import, dialogs
    MD + "dataImport/upload_file_black_24dp.svg": ms("upload_file"),
    MD + "dialog/123_sharp.svg": ms("123"),
    MD + "dialog/alternate_email.svg": ms("alternate_email"),
    MD + "dialog/bar_chart_black.svg": ms("bar_chart"),
    MD + "dialog/camera_white.svg": ms("photo_camera", W),
    MD + "dialog/google_classroom.svg": ms("co_present"),
    MD + "dialog/no_photography_black_24dp.svg": ms("no_photography"),
    MD + "dialog/open_in_new.svg": ms("open_in_new"),
    MD + "dialog/upload_black_24dp.svg": ms("upload"),
    # ---------------------------------------------------------------- dynamic style bar
    MD + "dynStylebar/baseline-format_color_text-24px.svg": ms("format_color_text"),
    MD + "dynStylebar/border_all-24px.svg": ms("border_all"),
    MD + "dynStylebar/border-all-variant.svg": ms("border_color"),
    MD + "dynStylebar/border_clear-24px.svg": ms("border_clear"),
    MD + "dynStylebar/border_inner-24px.svg": ms("border_inner"),
    MD + "dynStylebar/border_outer-24px.svg": ms("border_outer"),
    MD + "dynStylebar/check_border.svg": raw("check_on_swatch"),
    MD + "dynStylebar/color_black.svg": ms("palette"),
    MD + "dynStylebar/filling_bricks.svg": dr("fill_bricks"),
    MD + "dynStylebar/filling_chessboard.svg": dr("fill_chess"),
    MD + "dynStylebar/filling_cross_hatching.svg": dr("fill_crosshatch"),
    MD + "dynStylebar/filling_dots.svg": dr("fill_dots"),
    MD + "dynStylebar/filling_filled.svg": dr("fill_solid"),
    MD + "dynStylebar/filling_hatching.svg": dr("fill_hatch"),
    MD + "dynStylebar/filling_honeycomb.svg": dr("fill_honeycomb"),
    MD + "dynStylebar/filling_weaving.svg": dr("fill_weaving"),
    MD + "dynStylebar/fontspecific.svg": ms("special_character"),
    MD + "dynStylebar/format_align_center-24px.svg": ms("format_align_center"),
    MD + "dynStylebar/format_align_left-24px.svg": ms("format_align_left"),
    MD + "dynStylebar/format_align_right-24px.svg": ms("format_align_right"),
    MD + "dynStylebar/format_color_reset-24px.svg": ms("format_color_reset"),
    MD + "dynStylebar/format-text.svg": ms("text_fields"),
    MD + "dynStylebar/format_underlined-24px.svg": ms("format_underlined"),
    MD + "dynStylebar/ic_crop_black_24px.svg": ms("crop"),
    MD + "dynStylebar/ic_format_bold_black_24px.svg": ms("format_bold"),
    MD + "dynStylebar/ic_format_italic_black_24px.svg": ms("format_italic"),
    MD + "dynStylebar/ic_format_size_black_24px.svg": ms("format_size"),
    MD + "dynStylebar/ic_opacity_black_24px.svg": ms("opacity"),
    MD + "dynStylebar/no_filling.svg": dr("fill_none"),
    MD + "dynStylebar/stylingbar_line_dash_dot.svg": dr("line_dash_dot"),
    MD + "dynStylebar/stylingbar_line_dashed_long.svg": dr("line_dashed_long"),
    MD + "dynStylebar/stylingbar_line_dashed_short.svg": dr("line_dashed_short"),
    MD + "dynStylebar/stylingbar_line_dotted.svg": dr("line_dotted"),
    MD + "dynStylebar/stylingbar_line_solid.svg": dr("line_solid"),
    MD + "dynStylebar/stylingbar_point_cross_diag.svg": dr("point_cross"),
    MD + "dynStylebar/stylingbar_point_cross.svg": dr("point_plus"),
    MD + "dynStylebar/stylingbar_point_diamond_empty.svg": dr("point_diamond_empty"),
    MD + "dynStylebar/stylingbar_point_diamond_full.svg": dr("point_diamond_full"),
    MD + "dynStylebar/stylingbar_point_down.svg": dr("point_down"),
    MD + "dynStylebar/stylingbar_point_empty.svg": dr("point_circle"),
    MD + "dynStylebar/stylingbar_point_filled.svg": dr("point_dot"),
    MD + "dynStylebar/stylingbar_point_full.svg": dr("point_no_outline"),
    MD + "dynStylebar/stylingbar_point_left.svg": dr("point_left"),
    MD + "dynStylebar/stylingbar_point_right.svg": dr("point_right"),
    MD + "dynStylebar/stylingbar_point_up.svg": dr("point_up"),
    MD + "dynStylebar/vertical_align_bottom-24px.svg": ms("vertical_align_bottom"),
    MD + "dynStylebar/vertical_align_middle-24px.svg": ms("vertical_align_center"),
    MD + "dynStylebar/vertical_align_top-24px.svg": ms("vertical_align_top"),
    # ---------------------------------------------------------------- graphics view
    MD + "ev/axes_black.svg": dr("axes"),
    MD + "ev/baseline-error-24px.svg": ms("error"),
    MD + "ev/baseline-menu-24px.svg": ms("menu"),
    MD + "ev/drag_pad.svg": ms("drag_pan"),
    MD + "ev/grid_black.svg": dr("grid_cartesian"),
    MD + "ev/gridSVG.svg": dr("snap_to_grid"),
    MD + "ev/ic_fullscreen_black_18px.svg": ms("fullscreen", size=18),
    MD + "ev/ic_fullscreen_exit_black_18px.svg": ms("fullscreen_exit", size=18),
    MD + "ev/ic_refresh_black_24px.svg": ms("refresh"),
    MD + "ev/ic_settings_black_24px.svg": ms("settings"),
    MD + "ev/isometric.svg": dr("grid_isometric"),
    MD + "ev/minor_gridlines.svg": dr("grid_minor"),
    MD + "ev/point_capturing.svg": dr("snap_to_grid"),
    MD + "ev/polar.svg": dr("grid_polar"),
    MD + "ev/projection_glasses_black.svg": ms("eyeglasses"),
    MD + "ev/projection_oblique_black.svg": dr("proj_oblique"),
    MD + "ev/projection_orthographic_black.svg": dr("proj_orthographic"),
    MD + "ev/projection_perspective_black.svg": dr("proj_perspective"),
    MD + "ev/redo.svg": ms("redo"),
    MD + "ev/rotate_right.svg": ms("rotate_right"),
    MD + "ev/settings.svg": ms("settings"),
    MD + "ev/target.svg": ms("highlight"),  # the Notes spotlight tool
    MD + "ev/text_serif.svg": ms("serif"),
    MD + "ev/undo.svg": ms("undo"),
    # ------------------------------------------- style bar icons of the Mebis vendor theme
    MD + "fontawesome/arrow-line-large-filled-left.svg": dr("seg_arrow_filled"),
    MD + "fontawesome/arrow-line-large-filled-right.svg": dr("seg_arrow_filled", mirror=True),
    MD + "fontawesome/arrow-line-large-left.svg": dr("seg_arrow_outline"),
    MD + "fontawesome/arrow-line-large-right.svg": dr("seg_arrow_outline", mirror=True),
    MD + "fontawesome/arrow-line-left.svg": dr("seg_arrow"),
    MD + "fontawesome/arrow-line-right.svg": dr("seg_arrow", mirror=True),
    MD + "fontawesome/arrow-rotate-right.svg": fa("solid/arrow-rotate-right"),
    MD + "fontawesome/border-none.svg": fa("solid/border-none"),
    MD + "fontawesome/circle-line-filled-left.svg": dr("seg_circle_filled"),
    MD + "fontawesome/circle-line-filled-right.svg": dr("seg_circle_filled", mirror=True),
    MD + "fontawesome/circle-line-left.svg": dr("seg_circle_outline"),
    MD + "fontawesome/circle-line-right.svg": dr("seg_circle_outline", mirror=True),
    MD + "fontawesome/copy.svg": fa("regular/copy"),
    MD + "fontawesome/crossinglines.svg": dr("fill_crosshatch"),
    MD + "fontawesome/cube-line-filled-left.svg": dr("seg_square_filled"),
    MD + "fontawesome/cube-line-filled-right.svg": dr("seg_square_filled", mirror=True),
    MD + "fontawesome/cube-line-left.svg": dr("seg_square_outline"),
    MD + "fontawesome/cube-line-right.svg": dr("seg_square_outline", mirror=True),
    MD + "fontawesome/diagonal-off.svg": dr("fill_off"),
    MD + "fontawesome/diagonal.svg": dr("fill_hatch"),
    MD + "fontawesome/diamond-line-filled-left.svg": dr("seg_diamond_filled"),
    MD + "fontawesome/diamond-line-filled-right.svg": dr("seg_diamond_filled", mirror=True),
    MD + "fontawesome/diamond-line-left.svg": dr("seg_diamond_outline"),
    MD + "fontawesome/diamond-line-right.svg": dr("seg_diamond_outline", mirror=True),
    MD + "fontawesome/dots.svg": dr("fill_dots"),
    MD + "fontawesome/font-color.svg": ms("format_color_text"),
    MD + "fontawesome/honeycomb.svg": dr("fill_honeycomb"),
    MD + "fontawesome/horizontal-lines-3.svg": dr("lines_3"),
    MD + "fontawesome/horizontal-lines-4.svg": dr("lines_4"),
    MD + "fontawesome/horizontal-lines-6.svg": dr("lines_6"),
    MD + "fontawesome/horizontal-lines-dot-dash.svg": dr("lines_dot_dash"),
    MD + "fontawesome/pen-line.svg": fa("solid/pen"),
    MD + "fontawesome/scissors.svg": fa("solid/scissors"),
    MD + "fontawesome/short-line-left.svg": dr("seg_plain"),
    MD + "fontawesome/short-line-right.svg": dr("seg_plain"),
    MD + "fontawesome/spread-line-left.svg": dr("seg_crows_foot"),
    MD + "fontawesome/spread-line-right.svg": dr("seg_crows_foot", mirror=True),
    MD + "fontawesome/stop-line-left.svg": dr("seg_stop"),
    MD + "fontawesome/stop-line-right.svg": dr("seg_stop", mirror=True),
    MD + "fontawesome/table-heading-column.svg": dr("heading_column"),
    MD + "fontawesome/table-heading-row.svg": dr("heading_row"),
    MD + "fontawesome/table-rows.svg": fa("solid/table-list"),
    MD + "fontawesome/x-2.svg": fa("solid/subscript"),
    MD + "fontawesome/x-square.svg": fa("solid/superscript"),
    # ---------------------------------------------------------------- notes app (mow)
    MD + "mow/arrow-alt-circle-down.svg": ms("arrow_circle_down"),
    MD + "mow/baseline-folder_open-24px.svg": ms("folder_open"),
    MD + "mow/baseline-group-24px.svg": ms("group"),
    MD + "mow/baseline-groups-24px.svg": ms("groups"),
    MD + "mow/baseline-link-black-24px.svg": ms("link"),
    MD + "mow/baseline-link-white-24px.svg": ms("link", W),
    MD + "mow/baseline-lock-24px.svg": ms("lock"),
    MD + "mow/baseline-people-24px.svg": ms("group"),
    MD + "mow/baseline-public-24px.svg": ms("public"),
    MD + "mow/check_mark_white.svg": ms("check", W),
    MD + "mow/file_plus.svg": ms("note_add"),
    MD + "mow/file.svg": ms("description"),
    MD + "mow/ic_add_white_24px.svg": ms("add", W),
    MD + "mow/ic_view_module_24px.svg": ms("view_module"),
    MD + "mow/lightbulb_outline_black_24px.svg": ms("lightbulb"),
    MD + "mow/page_overview_bycs.svg": ms("grid_view"),
    MD + "mow/rename_box_black_24px.svg": ms("edit_square"),
    MD + "mow/toolbox/add_box.svg": ms("apps"),
    MD + "mow/toolbox/ellipse.svg": dr("ellipse"),
    MD + "mow/toolbox/freeform.svg": dr("freeform"),
    MD + "mow/toolbox/geogebra.svg": dr("logo"),
    MD + "mow/toolbox/line.svg": dr("curve"),
    MD + "mow/toolbox/mask.svg": dr("mask"),
    MD + "mow/toolbox/mouse_cursor.svg": ms("arrow_selector_tool"),
    MD + "mow/toolbox/parallel.svg": dr("parallelogram"),
    MD + "mow/toolbox/polygon.svg": dr("pentagon"),
    MD + "mow/toolbox/stadium.svg": dr("stadium"),
    MD + "mow/toolbox/text_fields.svg": ms("text_fields"),
    MD + "mow/toolbox/tool_shapes.svg": ms("shapes"),
    MD + "mow/video_player_black_opacity54_360px.png": raw("video_placeholder", png=(360, 202)),
    # ---------------------------------------------------------------- open file view
    MD + "openFileView/drive_icon_24px.svg": fa("brands/google-drive"),
    MD + "openFileView/folder_black_24dp.svg": ms("folder"),
    MD + "openFileView/link_black_24dp.svg": ms("link"),
    MD + "openFileView/login_black_24dp.svg": ms("login"),
    MD + "openFileView/visibility_black_24dp.svg": ms("visibility"),
    # ---------------------------------------------------------------- settings
    MD + "settings/axis_tick_major_minor.svg": dr("axis_tick_major_minor"),
    MD + "settings/axis_tick_major.svg": dr("axis_tick_major"),
    MD + "settings/axis_tick_off.svg": dr("axis_tick_off"),
    MD + "settings/cell_border_thick.svg": dr("cell_border_thick"),
    MD + "settings/cell_border_thin.svg": dr("cell_border_thin"),
    MD + "settings/format_text_clip_24dp.svg": ms("format_text_clip"),
    MD + "settings/format_text_wrap_24dp.svg": ms("format_text_wrap"),
    MD + "settings/ic_arrow_drop_down_black_24px.svg": ms("arrow_drop_down"),
    MD + "settings/ic_arrow_drop_up_black_24px.svg": ms("arrow_drop_up"),
    MD + "settings/no_border.svg": dr("border_none"),
    MD + "settings/rightAngleDot.svg": dr("right_angle_dot"),
    MD + "settings/rightAngleOff.svg": dr("right_angle_off"),
    MD + "settings/rightAngleRectangle.svg": dr("right_angle_rect"),
    MD + "settings/rightAngleStroke.svg": dr("right_angle_stroke"),
    MD + "settings/text_rotate_up_24dp.svg": ms("text_rotate_up"),
    MD + "settings/text_rotate_vertical_24dp.svg": ms("text_rotate_vertical"),
    MD + "settings/text_rotation_none_24dp.svg": ms("text_rotation_none"),
    MD + "settings/thick_border.svg": dr("border_thick"),
    MD + "settings/thin_border.svg": dr("border_thin"),
    # ---------------------------------------------------------------- tool bar and tabs
    MD + "toolBar/av_tab_graphing_black.svg": ms("function"),
    MD + "toolBar/baseline-table_chart-24px-black.svg": ms("table_chart"),
    MD + "toolBar/distribution.svg": dr("bell"),
    MD + "toolBar/ic_arrow_back_black_24px.svg": ms("arrow_back"),
    MD + "toolBar/ic_keyboard_arrow_down_black_24px.svg": ms("keyboard_arrow_down"),
    MD + "toolBar/ic_keyboard_arrow_left_black_24px.svg": ms("keyboard_arrow_left"),
    MD + "toolBar/move_white.svg": ms("arrow_selector_tool", W),
    MD + "toolBar/spreadsheet.svg": ms("table"),
    MD + "toolBar/tools_tab_black.svg": ms("category"),
    # ---------------------------------------------------------------- app and view icons
    C + "svg/web/menuIconsTransparent/menu_view_3d.svg": ms("deployed_code"),
    C + "svg/web/menuIconsTransparent/menu_view_algebra.svg": dr("graphing"),
    C + "svg/web/menuIconsTransparent/menu_view_cas.svg": ms("function"),
    C + "svg/web/menuIconsTransparent/menu_view_construction_protocol.svg": ms("list_alt"),
    C + "svg/web/menuIconsTransparent/menu_view_exam.svg": ms("assignment"),
    C + "svg/web/menuIconsTransparent/menu_view_graphics2.svg": dr("graphics2"),
    C + "svg/web/menuIconsTransparent/menu_view_graphics_extra.svg": dr("graphics_plane"),
    C + "svg/web/menuIconsTransparent/menu_view_graphics.svg": dr("geometry"),
    C + "svg/web/menuIconsTransparent/menu_view_probability.svg": dr("bell"),
    C + "svg/web/menuIconsTransparent/menu_view_spreadsheet.svg": ms("table"),
    C + "svg/web/menuIconsTransparent/menu_view_whiteboard.svg": ms("stylus_note"),
    # ---------------------------------------------------------------- keyboard
    KB + "abs.svg": kb("abs"),
    KB + "atomic_post.svg": kb("atomic_post"),
    KB + "atomic_pre.svg": kb("atomic_pre"),
    KB + "backspace.svg": ms("backspace", T),
    KB + "ceil.svg": kb("ceil"),
    KB + "definite_integral.svg": kb("definite_integral"),
    KB + "derivative.svg": kb("derivative"),
    KB + "e_power.svg": kb("e_power"),
    KB + "floor.svg": kb("floor"),
    KB + "fraction.svg": kb("fraction"),
    KB + "ic_keyboard_black_24px.svg": ms("keyboard"),
    KB + "ic_more_horiz_black_24px.svg": ms("more_horiz"),
    KB + "integral.svg": kb("integral"),
    KB + "inverse.svg": kb("inverse"),
    KB + "keyboard_arrowDown_black.svg": ms("keyboard_arrow_down", T),
    KB + "keyboard_arrowLeft_black.svg": ms("keyboard_arrow_left", T),
    KB + "keyboard_arrowRight_black.svg": ms("keyboard_arrow_right", T),
    KB + "keyboard_arrowUp_black.svg": ms("keyboard_arrow_up", T),
    KB + "keyboard_enter_black.svg": ms("keyboard_return", T),
    KB + "lim.svg": kb("lim"),
    KB + "log.svg": kb("log"),
    KB + "matrix_template.svg": kb("matrix_template"),
    KB + "mixed_number.svg": kb("mixed_number"),
    KB + "n_root.svg": kb("n_root"),
    KB + "point_template.svg": kb("point_template"),
    KB + "power.svg": kb("power"),
    KB + "product.svg": kb("product"),
    KB + "recurring_decimal.svg": kb("recurring_decimal"),
    KB + "shift_black.svg": ms("shift", T),
    KB + "shift_purple.svg": ms("shift-fill", L.PRIMARY),
    KB + "sqrt.svg": kb("sqrt"),
    KB + "square.svg": kb("square"),
    KB + "subscript.svg": kb("subscript"),
    KB + "sum.svg": kb("sum"),
    KB + "ten_power.svg": kb("ten_power"),
    KB + "vector.svg": kb("vector"),
    KB + "vector_template.svg": kb("vector_template"),
    # ---------------------------------------------------------------- raster icons
    C + "png/menu_view_graphics1.png": raw("graph_view", png=(24, 24)),
    C + "png/properties_position_corner1.png": raw("corner1", png=(24, 24)),
    C + "png/view_refresh.png": ms("refresh", png=(24, 24)),
    PNG + "algebra-view-tree-closed.png": ms("arrow_right", png=(16, 16)),
    PNG + "algebra-view-tree-open.png": ms("arrow_drop_down", png=(16, 16)),
    PNG + "arrow_go_previous_grey.png": ms("arrow_back", png=(24, 24)),
    PNG + "arrow-submenu-left.png": raw("pointer_left", png=(9, 18)),
    PNG + "arrow-submenu-right.png": raw("pointer_right", png=(9, 18)),
    PNG + "arrow-submenu-up.png": raw("pointer_up", png=(18, 9)),
    PNG + "button_cancel.png": ms("cancel", png=(24, 24)),
    PNG + "dialog-info.png": ms("info", L.PRIMARY, png=(32, 32)),
    PNG + "dialog-warning.png": ms("warning", L.WARNING, png=(32, 32)),
    PNG + "dockbar_triangle_left.png": ms("arrow_left", png=(16, 16)),
    PNG + "dockbar_triangle_right.png": ms("arrow_right", png=(16, 16)),
    PNG + "general/algebra_hidden.png": raw("marble_hidden", png=(16, 16)),
    PNG + "general/algebra_shown.png": raw("marble_shown", png=(16, 16)),
    PNG + "general/aux_folder.gif": ms("folder_special", png=(24, 24)),
    PNG + "general/color_chooser_check.png": raw("check_on_swatch", png=(12, 12)),
    PNG + "general/corner1.png": raw("corner1", png=(24, 24)),
    PNG + "general/corner2.png": raw("corner2", png=(24, 24)),
    PNG + "general/corner4.png": raw("corner4", png=(24, 24)),
    # fully transparent spacer: menu items without an icon keep the 24 px icon column
    PNG + "general/empty.gif": dict(kind="empty", png=(24, 24)),
    PNG + "general/geogebra64.png": raw("logo_color", png=(64, 64)),
    PNG + "general/osculating_circle.png": raw("osculating_circle", png=(24, 24)),
    PNG + "general/table.gif": ms("table", png=(24, 24)),
    PNG + "general/tangent_line.png": raw("tangent_line", png=(24, 24)),
    PNG + "general/xy_segments.png": raw("xy_segments", png=(24, 24)),
    PNG + "ggb_logo_back.png": raw("logo_color", png=(32, 32)),
    PNG + "menu-help.png": ms("help", png=(24, 24)),
    PNG + "menu_icons24/menu_view_exam.png": ms("assignment", png=(24, 24)),
    PNG + "menu_icons/menu-file.png": ms("draft", png=(24, 24)),
    PNG + "menu_icons/menu_view_graphics1.png": raw("graph_view", png=(24, 24)),
    PNG + "open-from-location_geogebratube.png": ms("cloud", png=(24, 24)),
    PNG + "open-from-location_googledrive.png": fa("brands/google-drive", png=(24, 24)),
    PNG + "open-from-location_local-storage.png": ms("computer", png=(24, 24)),
    PNG + "probability_calculator_cumulative_distribution.png": raw("cdf", png=(24, 24)),
    PNG + "question-mark.png": raw("missing_image", png=(32, 32)),
    PNG + "stylingbar/stylingbar_algebraview_sort_objects_by.png": ms("sort", png=(24, 24)),
    PNG + "stylingbar/stylingbar_data_analysis_show_2nd_plot.png": ms("splitscreen", png=(24, 24)),
    PNG + "stylingbar/stylingbar_data_analysis_show_data.png": ms("table_view", png=(24, 24)),
    PNG + "stylingbar/stylingbar_data_analysis_show_statistics.png": ms("functions", png=(24, 24)),
    PNG + "stylingbar/stylingbar_properties_object.png": ms("tune", png=(24, 24)),
    PNG + "toolbar-further-tools-icon.png": ms("arrow_drop_down", png=(24, 24)),
    PNG + "triangle_down.png": ms("arrow_drop_down", png=(16, 16)),
    PNG + "triangle_right.png": ms("arrow_right", png=(16, 16)),
    SPINNER: dict(kind="spinner", png=(40, 40)),
}


def mask_id(path):
    stem = re.sub(r"[^a-z0-9]+", "-", Path(path).stem.lower()).strip("-")
    return f"locus-{Path(path).parent.name.lower()}-{stem}"


def build_svg(path, spec):
    """Return (svg text, provenance source, provenance name)."""
    kind, name = spec["kind"], spec.get("name", "")
    color = spec.get("color", N)
    size = spec.get("size", 24)
    if kind == "ms":
        body = L.paths_body(L.material_paths(name))
        note = f'Material Symbols Outlined "{name}", Apache License 2.0, see THIRD_PARTY.md'
        return L.svg_doc(body, color, size, comment=note), "Material Symbols Outlined " + L.MS_VERSION, name
    if kind == "fa":
        body = L.paths_body(L.fa_paths(name))
        note = f'Font Awesome Free {L.FA_VERSION} "{name}" by Fonticons, Inc., CC BY 4.0, see THIRD_PARTY.md'
        return L.svg_doc(body, color, size, comment=note), "Font Awesome Free " + L.FA_VERSION, name
    if kind == "drawn":
        mid = mask_id(path)
        if name in drawn.MASKED_WITH_ID:
            ink = drawn.MASKED_WITH_ID[name](mid)
        else:
            ink = drawn.MASKED[name]()
        if spec.get("mirror"):
            ink = drawn.mirror(ink)
        return L.svg_doc(L.masked_body(ink, mid), color, size), "drawn", name
    if kind == "raw":
        return L.svg_doc(drawn.RAW[name](), "none", size), "drawn", name
    raise ValueError(kind)


# ------------------------------------------------------------------ rasters
_browser = None


def browser():
    global _browser
    if _browser is None:
        from playwright.sync_api import sync_playwright
        pw = sync_playwright().start()
        _browser = pw.chromium.launch(executable_path="/usr/bin/google-chrome")
    return _browser


def render(svg, w, h):
    """Render SVG markup into a w x h RGBA image with Chrome."""
    page = browser().new_page(viewport={"width": w, "height": h}, device_scale_factor=1)
    svg = re.sub(r'width="[^"]+" height="[^"]+"', f'width="{w}" height="{h}"', svg, count=1)
    if w != h:
        svg = svg.replace("<svg ", '<svg preserveAspectRatio="none" ', 1)
    page.set_content(f'<html><body style="margin:0;background:transparent">{svg}</body></html>')
    png = page.screenshot(clip={"x": 0, "y": 0, "width": w, "height": h}, omit_background=True)
    page.close()
    return Image.open(io.BytesIO(png)).convert("RGBA")


def video_placeholder(w, h):
    r = h * 0.16
    cx, cy = w / 2, h / 2
    tri = f"M{cx - r * 0.4} {cy - r * 0.6}L{cx + r * 0.6} {cy}L{cx - r * 0.4} {cy + r * 0.6}Z"
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
           f'<rect width="{w}" height="{h}" fill="#14181c" fill-opacity=".54"/>'
           f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#fff" fill-opacity=".9"/>'
           f'<path d="{tri}" fill="{L.TEXT}"/></svg>')
    return render(svg, w, h)


def spinner_frames(size, n=12):
    frames = []
    for i in range(n):
        a = 360 * i / n
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24">'
               f'<circle cx="12" cy="12" r="9" fill="none" stroke="{L.PRIMARY_TINT}" stroke-width="3"/>'
               f'<circle cx="12" cy="12" r="9" fill="none" stroke="{L.PRIMARY}" stroke-width="3"'
               f' stroke-linecap="round" stroke-dasharray="{2 * math.pi * 9 * 0.28:.2f} 100"'
               f' transform="rotate({a - 90} 12 12)"/></svg>')
        frames.append(render(svg, size, size))
    return frames


def to_gif_frame(img):
    """GIF has one transparent index and no alpha: composite on white, key out the background."""
    matte = Image.new("RGBA", img.size, (255, 255, 255, 255))
    matte.alpha_composite(img)
    rgb = matte.convert("RGB").quantize(colors=255, method=Image.Quantize.MEDIANCUT)
    pal = rgb.getpalette()[:765] + [0, 0, 0]
    out = Image.new("P", img.size, 255)
    out.putpalette(pal + [0] * (768 - len(pal)))
    alpha = img.getchannel("A")
    src = rgb.load()
    dst = out.load()
    a = alpha.load()
    for y in range(img.size[1]):
        for x in range(img.size[0]):
            dst[x, y] = src[x, y] if a[x, y] >= 24 else 255
    return out


def write_raster(path, spec, svg):
    w, h = spec["png"]
    out = ROOT / path
    kind = spec["kind"]
    if kind == "empty":
        img = Image.new("P", (w, h), 0)
        img.putpalette([0, 0, 0] * 256)
        img.save(out, format="GIF", transparency=0)
        return
    if kind == "spinner":
        frames = [to_gif_frame(f) for f in spinner_frames(w)]
        frames[0].save(out, format="GIF", save_all=True, append_images=frames[1:], duration=70,
                       loop=0, transparency=255, disposal=2)
        return
    if kind == "raw" and spec["name"] == "video_placeholder":
        img = video_placeholder(w, h)
    else:
        img = render(svg, w, h)
    if path.endswith(".gif"):
        to_gif_frame(img).save(out, format="GIF", transparency=255)
    else:
        img.save(out, format="PNG", optimize=True)


def provenance(spec, src, name):
    if spec["kind"] == "empty":
        return "drawn", "transparent spacer"
    if spec["kind"] == "spinner":
        return "drawn", "spinner"
    if spec["kind"] == "raw" and spec["name"] == "missing_image":
        return f"drawn, with Material Symbols Outlined {L.MS_VERSION}", "missing_image (question_mark)"
    return src, name


def main():
    listed = [p.strip() for p in (ROOT / "tools/images-sourced.txt").read_text().splitlines() if p.strip()]
    missing = sorted(set(listed) - set(SPEC))
    extra = sorted(set(SPEC) - set(listed))
    if missing or extra:
        sys.exit(f"spec mismatch\nmissing: {missing}\nextra: {extra}")
    rows = []
    for path in listed:
        spec = SPEC[path]
        svg, src, name = (None, "", "")
        if spec["kind"] not in ("empty", "spinner"):
            svg, src, name = build_svg(path, spec)
        if "png" in spec:
            write_raster(path, spec, svg)
        else:
            (ROOT / path).write_text(svg)
        src, name = provenance(spec, src, name)
        rows.append((path, src, name))
    tsv = "path\tsource\tupstream icon or drawn design\n" + "".join("\t".join(r) + "\n" for r in rows)
    (Path(__file__).parent / "sourced-icons.tsv").write_text(tsv)
    print(f"wrote {len(rows)} icons")


if __name__ == "__main__":
    main()
