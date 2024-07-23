# Weather Report

Este projeto fornece um sistema que contém 2 aplicações:

1. Um servidor socket que fornece dados
2. Um gerador de relatório em PDF, que lê dados do servidor socket

## Requisitos

- Anaconda
- python

## Instalação

*Ambos projetos usam python.*

Criando o ambiente virtual python:

```bash
conda create -n weather_report python=3.12
conda activate weather_report
```

## Executar

### Maildev

```bash
docker-compose up -d maildev
```

### Data_service

Docker:

```bash
docker-compose up -d data_service
```

Desenvolvimento local:

```bash
cd src
pip install -r requirements.txt
python -m data_service -d
```

> A flag `-d` `--detach` significa que você pode usar Ctrl-C para encerrar o servidor
> Uma opção conveniente para desenvolvimento.

## Sobre

### Aplicação 1 - Servidor TCP

Servidor de dados via TCP, garantindo performance, baixa latência e um canal de mão dupla para comunicação.

### Aplicação 2 - Gerador de relatório
