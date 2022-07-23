from time import sleep

from main import FeatureToggles

feature_toggles = FeatureToggles('/fx8/mfe', ['fx8_mfe_cadastrar_mfe'])
feature_toggles2 = FeatureToggles('/fx8/mfe2', ['fx8_mfe2_deletar_mfe'])

feature_toggles.is_authorize('cadastrar_mfe')
print('\n'*1)
feature_toggles2.is_authorize('cadastrar_mfe')
print('\n'*1)
sleep(5)
feature_toggles.is_authorize('cadastrar_mfe')
print('\n'*1)
feature_toggles2.is_authorize('cadastrar_mfe')
print('\n'*1)
sleep(5)
feature_toggles.is_authorize('cadastrar_mfe')
print('\n'*1)
feature_toggles2.is_authorize('cadastrar_mfe')
print('\n'*1)
