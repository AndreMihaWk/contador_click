# Contador de Visitantes

Conta, por webcam, as pessoas que visitam o estande.

- Você desenha com o mouse a área do estande na imagem da câmera.
- Cada pessoa que fica dentro dessa área conta como **1 visitante**, uma única vez.
- Tudo fica num banco SQLite local.
- O telão mostra os visitantes de **hoje** e o **total acumulado** de todos os dias em que a contagem funcionou.

## Instalação (uma vez)

1. Instale o Python 3 de [python.org](https://www.python.org/downloads/), que traz o comando `py`.
2. Dê dois cliques em **`instalar.bat`**. Leva alguns minutos.

Na primeira vez que o sistema rodar, ele baixa sozinho o modelo `yolo11n.pt` (~6 MB), por isso precisa de internet nesse momento.

## Uso

1. Dê dois cliques em **`iniciar.bat`**. O telão abre em tela cheia no Edge; para sair, use `Alt+F4`.
2. Com a contagem parada, o telão mostra três botões:
   - **✏️ Área da Câmera**: abre a imagem da webcam. Clique e arraste para desenhar a área do estande e clique em **Salvar área**.
   - **📊 Relatório**: mostra a quantidade de cada dia e, no final, o total de visitantes. Também permite baixar o CSV de cada dia ou o relatório completo.
   - **▶ Iniciar Contagem**: liga a contagem. A imagem da câmera aparece no canto do telão.
3. Durante a contagem, o mesmo botão vira **■ Encerrar Contagem**. Ao encerrar, o relatório do dia é salvo em `relatorios/relatorio_AAAA-MM-DD.csv`.

Outros comportamentos:
- **Virada do dia:** o relatório do dia anterior é fechado sozinho. Ele é gerado quando o dia vira com o sistema aberto, ou na primeira vez que o sistema abre num dia novo.
- **Reinício do PC:** se o computador reiniciar com a contagem ligada, ela volta ligada sozinha.
- **Ligar junto com o Windows:** pressione `Win+R`, digite `shell:startup` e coloque nessa pasta um atalho para o `iniciar.bat`.

| Endereço | O que mostra |
|---|---|
| http://127.0.0.1:5000 | Telão |
| http://127.0.0.1:5000/camera | Desenhar a área de captação |
| http://127.0.0.1:5000/relatorio | Relatório por dia e total |

## Configuração (`config.json`)

| Campo | Para que serve |
|---|---|
| `camera_indice` | Número da webcam (0, 1, 2...). Neste PC, 0 é a câmera infravermelha e 1 a colorida. Troque se ligar outra webcam. |
| `area` | Área de captação `[x1, y1, x2, y2]` em fração da imagem (0 a 1). É gravada pela página de desenho, não precisa editar à mão. |
| `tempo_minimo_s` | Quantos segundos a pessoa precisa ficar dentro da área para contar. Aumente para não contar quem só passa pela beirada. |
| `confianca_minima` | De 0 a 1. Aumente se contar coisas que não são pessoas; diminua se deixar pessoas passarem. |
| `porta` | Porta do servidor (padrão 5000). Se mudar, ajuste também o `iniciar.bat`. |

Mudanças nesses campos (menos `area`) valem depois de reiniciar o sistema.

## Estrutura

```
app.py                 servidor Flask + rotas da API
contador/db.py         banco SQLite (dados/contador.db)
contador/camera.py     webcam, detecção de pessoas (YOLO) e contagem na área
contador/relatorio.py  virada do dia e geração dos CSVs
web/                   telão, relatório e página de desenho da área
```
