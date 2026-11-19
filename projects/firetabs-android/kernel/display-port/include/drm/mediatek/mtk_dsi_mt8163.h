/* SPDX-License-Identifier: GPL-2.0-only */
#ifndef DRM_MEDIATEK_MT8163_PANEL_LANES_H
#define DRM_MEDIATEK_MT8163_PANEL_LANES_H
struct mipi_dsi_device;
/* Active host only. Exit lane ULPM after panel rails settle, before reset. */
int mtk_dsi_mt8163_prepare_lanes(struct mipi_dsi_device *device);
int mtk_dsi_mt8163_unprepare_lanes(struct mipi_dsi_device *device);
#endif
