import re, pathlib
base = pathlib.Path('android/app/src/main')
mf = base / 'AndroidManifest.xml'
s = mf.read_text()
if 'screenOrientation' not in s:
    s = s.replace('<activity', '<activity\n            android:screenOrientation="sensorLandscape"\n            android:hardwareAccelerated="true"', 1)
if 'ACCESS_NETWORK_STATE' not in s:
    s = s.replace('</manifest>', '    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />\n</manifest>')
mf.write_text(s)
java = base / 'java/com/ps1strike/game/MainActivity.java'
java.write_text('''package com.ps1strike.game;

import android.os.Build;
import android.os.Bundle;
import android.view.WindowManager;
import androidx.core.view.WindowCompat;
import androidx.core.view.WindowInsetsCompat;
import androidx.core.view.WindowInsetsControllerCompat;
import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {
  @Override
  public void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);
    getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
    if (Build.VERSION.SDK_INT >= 28) {
      getWindow().getAttributes().layoutInDisplayCutoutMode = WindowManager.LayoutParams.LAYOUT_IN_DISPLAY_CUTOUT_MODE_SHORT_EDGES;
    }
    WindowCompat.setDecorFitsSystemWindows(getWindow(), false);
    hideBars();
    try { getBridge().getWebView().getSettings().setMediaPlaybackRequiresUserGesture(false); } catch (Exception e) { }
  }
  @Override
  public void onWindowFocusChanged(boolean hasFocus) {
    super.onWindowFocusChanged(hasFocus);
    if (hasFocus) hideBars();
  }
  @Override
  public void onResume() {
    super.onResume();
    hideBars();
  }
  private void hideBars() {
    WindowInsetsControllerCompat c = WindowCompat.getInsetsController(getWindow(), getWindow().getDecorView());
    c.setSystemBarsBehavior(WindowInsetsControllerCompat.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE);
    c.hide(WindowInsetsCompat.Type.systemBars());
  }
}
''')

# ---- custom launcher icon: put icon.png (square, 512x512 or bigger) in the repo root
import os, subprocess, sys, shutil
icon = None
for cand in ('icon.png', 'Icon.png', 'icon.PNG'):
    if os.path.exists(cand): icon = cand; break
if icon:
    try:
        from PIL import Image
    except ImportError:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--quiet', 'pillow']); from PIL import Image
    im = Image.open(icon).convert('RGBA')
    side = min(im.size); im = im.crop(((im.width - side) // 2, (im.height - side) // 2, (im.width - side) // 2 + side, (im.height - side) // 2 + side))
    for d, px in (('mdpi', 48), ('hdpi', 72), ('xhdpi', 96), ('xxhdpi', 144), ('xxxhdpi', 192)):
        folder = base / 'res' / ('mipmap-' + d)
        folder.mkdir(parents=True, exist_ok=True)
        r = im.resize((px, px), Image.LANCZOS)
        for n in ('ic_launcher.png', 'ic_launcher_round.png', 'ic_launcher_foreground.png'):
            r.save(folder / n)
    any26 = base / 'res' / 'mipmap-anydpi-v26'
    if any26.exists(): shutil.rmtree(any26)
    print('icon applied from', icon)
else:
    print('no icon.png found, default icon kept')
print('patched')
