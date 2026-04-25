# Projeto: Monitor de Temperatura com Alerta
# Placa: ESP32 
# Simulação: Wokwi
# Aprendi no curso que sistemas embarcados trabalham com leitura de sensores
# e controle de atuadores (LEDs, buzzers, etc). Aqui usei o que estudei
# sobre GPIO, temporizadores nao-bloqueantes e logica de estados.

import machine # pyright: ignore[reportMissingImports]
import time
import dht # pyright: ignore[reportMissingImports]

# pinos '
# defini os pinos de acordo com o diagrama que montei no wokwi
PINO_SENSOR  = 4
PINO_LED_OK  = 25   # verde = temperatura normal
PINO_LED_MED = 26   # amarelo = temperatura alta
PINO_LED_ERR = 27   # vermelho = temperatura critica
PINO_BOTAO   = 14   # botao pra reconhecer o alarme

# limiares de temperatura 
TEMP_ALTA    = 28.0
TEMP_CRITICA = 35.0

# intervalos de tempo (em ms) 
# aprendi que usar ticks_ms evita travar o programa com sleep()
INTERVALO_SENSOR = 2000
INTERVALO_PISCA  = 500
DEBOUNCE         = 200

# estados possiveis do sistema
NORMAL  = "NORMAL"
ALERTA  = "ALERTA"
CRITICO = "CRITICO"
ERRO    = "ERRO"

# inicializando hardware
sensor  = dht.DHT22(machine.Pin(PINO_SENSOR))
led_ok  = machine.Pin(PINO_LED_OK,  machine.Pin.OUT)
led_med = machine.Pin(PINO_LED_MED, machine.Pin.OUT)
led_err = machine.Pin(PINO_LED_ERR, machine.Pin.OUT)
botao   = machine.Pin(PINO_BOTAO, machine.Pin.IN, machine.Pin.PULL_UP)

# variaveis de controle
estado_atual   = NORMAL
alarme_ack     = False      # True quando operador reconhece o alarme critico
led_err_toggle = False      # pra controlar o pisca-pisca

tick_sensor = 0
tick_pisca  = 0
tick_botao  = 0


# funcoes auxiliares 

def apagar_leds():
    led_ok.value(0)
    led_med.value(0)
    led_err.value(0)

def acender_led(estado):
    apagar_leds()
    if estado == NORMAL:
        led_ok.value(1)
    elif estado == ALERTA:
        led_med.value(1)
    elif estado == CRITICO or estado == ERRO:
        led_err.value(1)

def verificar_estado(temp):
    # logica de classificacao baseada nos limiares definidos
    if temp >= TEMP_CRITICA:
        return CRITICO
    elif temp >= TEMP_ALTA:
        return ALERTA
    else:
        return NORMAL

def ler_dht22():
    # tentei fazer sem try/except primeiro mas o sensor as vezes falha
    # entao coloquei tratamento de erro como aprendi em fundamentos de python
    try:
        sensor.measure()
        return sensor.temperature(), sensor.humidity()
    except OSError:
        return None, None

def imprimir(msg):
    # uso o tempo em segundos como prefixo pra facilitar leitura no serial
    t = time.ticks_ms() // 1000
    print("[{}s] {}".format(t, msg))


# loop principal

def main():
    global estado_atual, alarme_ack
    global tick_sensor, tick_pisca, tick_botao
    global led_err_toggle

    imprimir("Sistema iniciado")
    imprimir("Alerta em {}C | Critico em {}C".format(TEMP_ALTA, TEMP_CRITICA))
    acender_led(NORMAL)

    while True:
        agora = time.ticks_ms()

        # 1. leitura do sensor a cada INTERVALO_SENSOR ms
        if time.ticks_diff(agora, tick_sensor) >= INTERVALO_SENSOR:
            tick_sensor = agora

            temp, umid = ler_dht22()

            if temp is None:
                if estado_atual != ERRO:
                    estado_atual = ERRO
                    acender_led(ERRO)
                    imprimir("Erro na leitura do sensor!")
            else:
                novo = verificar_estado(temp)

                if novo != estado_atual:
                    imprimir("Estado: {} -> {}".format(estado_atual, novo))
                    estado_atual = novo
                    alarme_ack   = False
                    acender_led(estado_atual)

                imprimir("Temp: {}C | Umid: {}%".format(temp, umid))

        # 2. pisca led vermelho quando critico e alarme nao reconhecido
        if estado_atual == CRITICO and not alarme_ack:
            if time.ticks_diff(agora, tick_pisca) >= INTERVALO_PISCA:
                tick_pisca     = agora
                led_err_toggle = not led_err_toggle
                led_err.value(1 if led_err_toggle else 0)

        # 3. botao com debounce pra reconhecer o alarme
        # pull_up = logica invertida: 0 quando pressionado
        if botao.value() == 0:
            if time.ticks_diff(agora, tick_botao) >= DEBOUNCE:
                tick_botao = agora

                if estado_atual == CRITICO:
                    alarme_ack = True
                    led_err.value(1)
                    imprimir("Alarme reconhecido! LED fixo.")
                else:
                    imprimir("Botao pressionado.")


main()