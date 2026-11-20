/* SPDX-License-Identifier: Apache-2.0 */
package com.valethon.readiness;

import android.app.Activity;
import android.os.Bundle;
import android.webkit.WebView;
import android.widget.LinearLayout;
import android.widget.TextView;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;

/** Manually launched, permission-free offline UI check. Never a boot dependency. */
public final class ReadinessActivity extends Activity {
    private WebView web;

    @Override public void onCreate(Bundle saved) {
        super.onCreate(saved);
        LinearLayout layout = new LinearLayout(this);
        layout.setOrientation(LinearLayout.VERTICAL);
        TextView status = new TextView(this);
        status.setTextSize(20);
        status.setPadding(24, 24, 24, 24);
        status.setText("Valethon app started. Loading offline WebView…");
        layout.addView(status);
        setContentView(layout);
        try {
            web = new WebView(this);
            web.getSettings().setJavaScriptEnabled(true);
            web.getSettings().setAllowFileAccess(false);
            web.getSettings().setAllowContentAccess(false);
            web.getSettings().setBlockNetworkLoads(true);
            layout.addView(web, new LinearLayout.LayoutParams(-1, 0, 1));
            try (InputStream input = getAssets().open("readiness.html")) {
                String html = new String(input.readAllBytes(), StandardCharsets.UTF_8);
                web.loadDataWithBaseURL("https://readiness.invalid/", html,
                        "text/html", "UTF-8", null);
            }
            status.setText("Offline WebView: tap the nine tiles, type below, then leave with Back.");
        } catch (Exception | LinkageError failure) {
            status.setText("WebView unavailable: " + failure.getClass().getSimpleName()
                    + ". Launcher and ADB remain independent.");
        }
    }

    @Override protected void onPause() {
        if (web != null) web.onPause();
        super.onPause();
    }

    @Override protected void onResume() {
        super.onResume();
        if (web != null) web.onResume();
    }

    @Override protected void onDestroy() {
        if (web != null) {
            ((LinearLayout) web.getParent()).removeView(web);
            web.destroy();
            web = null;
        }
        super.onDestroy();
    }
}
