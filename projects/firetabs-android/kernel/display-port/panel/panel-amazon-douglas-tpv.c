// SPDX-License-Identifier: GPL-2.0-only
/* Douglas TPV production panel; commands/power order from the pinned4.9 driver.
 * The legacy nt35521 wrapper serves multiple panel ICs; do not infer a TPV IC.
 * Only the observed TPV variant is matched. Other vendors need their own data.
 */
#include <linux/delay.h>
#include <linux/gpio/consumer.h>
#include <linux/module.h>
#include <linux/of.h>
#include <linux/regulator/consumer.h>
#include <drm/drm_connector.h>
#include <drm/drm_mipi_dsi.h>
#include <drm/drm_modes.h>
#include <drm/drm_panel.h>
#include <drm/mediatek/mtk_dsi_mt8163.h>
#include "douglas_tpv_core.h"

struct douglas_tpv {
 struct drm_panel panel;
 struct mipi_dsi_device *dsi;
 struct regulator *vddio;
 struct gpio_desc *power,*reset;
 struct douglas_tpv_state state;
 struct douglas_tpv_io io;
};
static int tpv_supply(void *ctx,int on)
{
 struct douglas_tpv *p=ctx;
 return on?regulator_enable(p->vddio):regulator_disable(p->vddio);
}
static void tpv_power(void *ctx,int on)
{
 struct douglas_tpv *p=ctx;gpiod_set_value_cansleep(p->power,on);
}
static void tpv_reset(void *ctx,int asserted)
{
 struct douglas_tpv *p=ctx;gpiod_set_value_cansleep(p->reset,asserted);
}
static void tpv_delay(void *ctx,unsigned int milliseconds)
{
 (void)ctx;msleep(milliseconds);
}
static int tpv_lanes_ready(void *ctx)
{
 struct douglas_tpv *p=ctx;return mtk_dsi_mt8163_prepare_lanes(p->dsi);
}
static int tpv_lanes_down(void *ctx)
{
 struct douglas_tpv *p=ctx;return mtk_dsi_mt8163_unprepare_lanes(p->dsi);
}
static long tpv_write(void *ctx,const unsigned char *data,unsigned int length)
{
 struct douglas_tpv *p=ctx;
 return mipi_dsi_dcs_write_buffer(p->dsi,data,length);
}
static int tpv_prepare(struct drm_panel *panel)
{
 struct douglas_tpv *p=container_of(panel,struct douglas_tpv,panel);
 return douglas_tpv_prepare(&p->state,&p->io);
}
static int tpv_disable(struct drm_panel *panel)
{
 struct douglas_tpv *p=container_of(panel,struct douglas_tpv,panel);
 douglas_tpv_disable(&p->state,&p->io);return 0;
}
static int tpv_unprepare(struct drm_panel *panel)
{
 struct douglas_tpv *p=container_of(panel,struct douglas_tpv,panel);
 return douglas_tpv_unprepare(&p->state,&p->io);
}
/* Preserve TPV porches and the working234MHz DDR PLL (468Mbps,4 lanes,RGB888).
 * 78000kHz preserves that link rate through this host's pixelclock*bpp/lanes.
 * It is not an invented60Hz mode; actual refresh/electrical timing needs hardware.
 */
static const struct drm_display_mode tpv_mode={
 .clock=78000,.hdisplay=800,.hsync_start=828,.hsync_end=854,.htotal=882,
 .vdisplay=1280,.vsync_start=1301,.vsync_end=1305,.vtotal=1320,
 .width_mm=108,.height_mm=172,
};
static int tpv_get_modes(struct drm_panel *panel,struct drm_connector *connector)
{
 struct drm_display_mode *mode=drm_mode_duplicate(connector->dev,&tpv_mode);
 if(!mode)return -ENOMEM;
 drm_mode_set_name(mode);mode->type=DRM_MODE_TYPE_DRIVER|DRM_MODE_TYPE_PREFERRED;
 drm_mode_probed_add(connector,mode);
 connector->display_info.width_mm=tpv_mode.width_mm;
 connector->display_info.height_mm=tpv_mode.height_mm;
 return 1;
}
static const struct drm_panel_funcs tpv_funcs={
 .prepare=tpv_prepare,.disable=tpv_disable,.unprepare=tpv_unprepare,.get_modes=tpv_get_modes,
};
static int tpv_probe(struct mipi_dsi_device *dsi)
{
 struct device *dev=&dsi->dev;struct douglas_tpv *p;int ret;
 p=devm_drm_panel_alloc(dev,struct douglas_tpv,panel,&tpv_funcs,DRM_MODE_CONNECTOR_DSI);
 if(IS_ERR(p))return PTR_ERR(p);
 p->dsi=dsi;
 p->vddio=devm_regulator_get(dev,"vddio");
 if(IS_ERR(p->vddio))return dev_err_probe(dev,PTR_ERR(p->vddio),"vddio supply\n");
 ret=drm_panel_of_backlight(&p->panel);if(ret)return ret;
 p->reset=devm_gpiod_get(dev,"reset",GPIOD_OUT_HIGH);
 if(IS_ERR(p->reset))return dev_err_probe(dev,PTR_ERR(p->reset),"panel reset GPIO\n");
 /* Assert reset before dropping any inherited panel power. */
 msleep(15);
 p->power=devm_gpiod_get(dev,"power",GPIOD_OUT_LOW);
 if(IS_ERR(p->power))return dev_err_probe(dev,PTR_ERR(p->power),"panel power GPIO\n");
 p->io=(struct douglas_tpv_io){tpv_supply,tpv_power,tpv_reset,tpv_delay,tpv_lanes_ready,tpv_lanes_down,tpv_write,p};
 /* Host clocks first; core powers rails, requests LP11, then resets panel. */
 p->panel.prepare_prev_first=true;
 dsi->lanes=4;dsi->format=MIPI_DSI_FMT_RGB888;
 dsi->mode_flags=MIPI_DSI_MODE_VIDEO|MIPI_DSI_MODE_LPM|MIPI_DSI_CLOCK_NON_CONTINUOUS;
 mipi_dsi_set_drvdata(dsi,p);drm_panel_add(&p->panel);
 ret=mipi_dsi_attach(dsi);
 if(ret)drm_panel_remove(&p->panel);
 return ret;
}
static void tpv_remove(struct mipi_dsi_device *dsi)
{
 struct douglas_tpv *p=mipi_dsi_get_drvdata(dsi);int ret;
 drm_panel_disable(&p->panel);drm_panel_unprepare(&p->panel);
 ret=mipi_dsi_detach(dsi);if(ret)dev_err(&dsi->dev,"DSI detach: %d\n",ret);
 drm_panel_remove(&p->panel);
}
static void tpv_shutdown(struct mipi_dsi_device *dsi)
{
 struct douglas_tpv *p=mipi_dsi_get_drvdata(dsi);
 drm_panel_disable(&p->panel);drm_panel_unprepare(&p->panel);
}
static const struct of_device_id tpv_of_match[]={
 { .compatible="amazon,douglas-tpv-panel" },{}
};
MODULE_DEVICE_TABLE(of,tpv_of_match);
static struct mipi_dsi_driver tpv_driver={
 .probe=tpv_probe,.remove=tpv_remove,.shutdown=tpv_shutdown,
 .driver={.name="panel-amazon-douglas-tpv",.of_match_table=tpv_of_match},
};
module_mipi_dsi_driver(tpv_driver);
MODULE_DESCRIPTION("Amazon Douglas TPV production panel");
MODULE_LICENSE("GPL");
