# Monitor de Temperatura com Alerta Visual

- Nome: Raíssa de Brito Duarte
- GitHub: raissabdrt

# 1. Visão Geral

Esse projeto surgiu da ideia do "Projeto Prático: Monitor de Ambiente Interativo" que estudei no curso. Quis implementar algo parecido: um sistema que lê temperatura e umidade de um sensor DHT22, classifica o ambiente em três níveis (normal, alerta e crítico) e acende LEDs de acordo com cada situação. Também adicionei um botão para o operador poder reconhecer o alarme quando a temperatura está crítica. A simulação roda no Wokwi com uma placa ESP32 DevKit C v4.

# 2. Arquitetura do Sistema

O programa principal fica em `src/main.py` e roda num loop infinito.
O ponto mais importante que aprendi no módulo de Temporizadores e Interrupções é que não devo usar `sleep()` dentro do loop principal, porque isso trava o programa e ele deixa de responder a outros eventos (como o botão).

Por isso usei `time.ticks_ms()` com `ticks_diff()` para controlar os intervalos de forma não-bloqueante. O sistema tem três "tarefas" rodando no mesmo loop:
loop principal:
- tarefa 1: leitura do sensor (a cada 2 segundos)
- tarefa 2: pisca-pisca do LED vermelho (a cada 500ms, só no estado CRITICO)
- tarefa 3: leitura do botão com debounce (200ms)

A lógica de estados ficou assim:

 Estado    Condição               LED          

 NORMAL   temp < 28°C            Verde fixo   
 ALERTA   28°C ≤ temp < 35°C     Amarelo fixo 
 CRITICO  temp ≥ 35°C            Vermelho piscando 
 ERRO     falha no sensor        Vermelho fixo 

# 3. Componentes Utilizados

Montei o circuito no `diagram.json` com os seguintes componentes:

- ESP32 DevKit C v4: esp - microcontrolador principal 
- DHT22: dht1 - sensor de temperatura e umidade
- LED verde: led_ok - indica temperatura normal                 
- LED amarelo: led_med - indica temperatura alta (alerta)
- LED vermelho: led_err  - indica temperatura crítica ou erro
- Resistores 220Ω (3x): r1,r2,r3 - proteção dos LEDs (Lei de Ohm)
- Push-button: btn1 - reconhecimento manual do alarme

Pinos usados no ESP32:

 GPIO  Componente        

 4     DHT22 (dados)     
 25    LED verde         
 26    LED amarelo       
 27    LED vermelho      
 14    Botão (pull-up) 

Os resistores de 220Ω foram calculados considerando 3.3V do ESP32 e tensão de forward dos LEDs de ~2V, resultando em ~6mA por LED, dentro do limite seguro.

# 4. Decisões Técnicas

- Temporização não-bloqueante: a principal decisão foi não usar `sleep()` no loop. Aprendi no módulo de Temporizadores que o correto é usar ticks para gerenciar múltiplos eventos ao mesmo tempo sem bloquear a CPU.

- Pull-up interno no botão: usei `machine.Pin.PULL_UP` para não precisar de resistor externo. Com pull-up, o botão lê 0 quando pressionado (lógica invertida), o que é padrão em microcontroladores.

- Debounce por software: botões mecânicos geram ruído na leitura. Resolvi isso verificando se passaram pelo menos 200ms desde o último evento antes de processar o pressionamento.

- Constantes no início do arquivo: coloquei todos os pinos e limiares como constantes nomeadas no topo, assim fica fácil adaptar para outro hardware sem precisar mexer na lógica.

- Tratamento de erro do sensor: o DHT22 pode falhar na leitura às vezes. Aprendi em Fundamentos de Python a usar try/except para não
deixar o programa travar nesses casos.

# 5. Resultados

O sistema funcionou conforme esperado na simulação:

- LED verde acende quando a temperatura configurada no DHT22 está abaixo de 28°C
- LED amarelo acende entre 28°C e 34.9°C
- LED vermelho pisca quando atinge 35°C ou mais
- Ao pressionar o botão no estado crítico, o LED para de piscar e fica fixo
- O monitor serial mostra as leituras a cada 2 segundos com o timestamp
- O pipeline do GitHub Actions executou com sucesso 


# 6. Comentários Finais

Foi meu primeiro contato real com simulação de hardware. Tive um pouco de dificuldade no início para entender como o `diagram.json` funciona, mas depois que entendi a estrutura de `parts` e `connections` ficou mais tranquilo. Se tivesse mais tempo, gostaria de adicionar um display OLED para mostrar os valores direto no circuito, e talvez enviar os dados via MQTT como vimos no módulo de Envio de Dados Industriais. O maior aprendizado foi entender na prática por que não se usa `sleep()` em sistemas embarcados reais, o que faz todo sentido agora. 