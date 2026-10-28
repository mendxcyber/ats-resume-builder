# ATS Resume Builder

Gerador de currículos PDF em Python, extraído de uma plataforma local de candidaturas. Usa os dados declarados pelo usuário e perfis de apresentação por área, sem depender de API de IA.

## Como funciona

1. Lê o perfil e a vaga em JSON.
2. Escolhe uma área por correspondência simples de termos: tecnologia, atendimento, administrativo ou comercial.
3. Usa o resumo e a ordem de experiências configurados para essa área.
4. Gera um PDF de uma coluna, com texto selecionável e seções convencionais.

O gerador não interpreta livremente todos os requisitos da vaga. A personalização atual é baseada em regras e em textos previamente definidos pelo usuário. Não inventa experiências nem acrescenta certificações.

## Instalação e uso

Requisito: Python 3.12.

```bash
git clone https://github.com/mendxcyber/ats-resume-builder.git
cd ats-resume-builder
python -m venv .venv
# Ative a .venv conforme seu sistema.
python -m pip install -r requirements.txt
python ats_resume.py --candidate examples/candidate.json --job examples/job.json --output generated/CV.pdf
```

Os exemplos são fictícios. Faça uma cópia privada e preencha apenas informações verdadeiras. O campo `resumos` permite escrever versões por área, e `ordem_experiencias` referencia os IDs declarados em `experiencias`. Localidade, competências e idiomas também vêm do perfil.

O programa tenta duas configurações de fonte para caber em uma página. Um perfil extenso ainda pode gerar mais páginas; revise o resultado. Nomes e campos muito longos também exigem revisão visual.

## Testes

```bash
python -m unittest discover -s tests -v
```

Os testes verificam extração de texto, seleção do resumo, ordem das experiências, uma página no exemplo e ausência de competências não declaradas.

## Limitações

“ATS friendly” descreve a estrutura do documento, não uma garantia de aprovação ou uma pontuação em todos os sistemas. Não existe comparação automática com a experiência real do candidato. Esta edição não envia candidaturas e não coleta vagas.

## Origem

Parte do [JobFlow Local](https://github.com/mendxcyber/jobflow-local), separada para facilitar estudo, uso e manutenção. Desenvolvido por **mendxcyber**, com apoio de IA. Código sob MIT; ReportLab e pypdf mantêm suas licenças.

Veja [o anúncio do projeto](docs/ANNOUNCEMENT.md).
