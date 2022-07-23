from time import sleep

from main import FeatureToggles

feat = FeatureToggles('/fx8/mfe', ['fx8_mfe_cadastrar_mfe'])

print('#'*10, feat.has_access('cadastrar_mfe'))
sleep(10)
print('#'*10, feat.has_access('cadastrar_mfe'))
sleep(5)
print('#'*10, feat.has_access('cadastrar_mfe'))
