# Correção de Conflito de Dependências

## Problema Identificado

Durante a instalação das dependências do projeto, foi identificado um conflito de versões entre:

1. **pydantic-settings==2.1.0** (versão fixada no requirements.txt original)
2. **docling>=1.0.0** (que requer pydantic-settings>=2.3.0,<3.0.0)
3. **docling-parse>=1.0.0** e **docling-core>=1.0.0** (dependências relacionadas)

### Mensagem de Erro Original

```
ERROR: Cannot install -r requirements.txt (line 21), docling-parse>=1.0.0,
docling==2.4.2 and pydantic-settings==2.1.0 because these package versions
have conflicting dependencies.
ERROR: ResolutionImpossible
```

## Explicação Técnica

O **pip** utiliza um resolvedor de dependências que tenta encontrar versões compatíveis de todos os pacotes solicitados. Quando há conflitos irreconciliáveis, a instalação falha.

No nosso caso:
- A biblioteca **docling** (essencial para o UC2 - detecção de parágrafos) foi atualizada para versões mais recentes que exigem **pydantic-settings>=2.3.0**
- O requirements.txt original fixava **pydantic-settings==2.1.0** (versão incompatível)
- Isso criou um impasse: não é possível instalar ambas as bibliotecas com essas restrições

## Mudanças Aplicadas

Para resolver o conflito, foram feitas as seguintes alterações no `requirements.txt`:

### 1. Pydantic e Pydantic-Settings

**Antes:**
```
pydantic==2.5.3
pydantic-settings==2.1.0
```

**Depois:**
```
pydantic>=2.5.3,<3.0.0
pydantic-settings>=2.3.0,<3.0.0
```

**Explicação educativa:**
- Mudamos de versão **fixa** (==) para versão com **range** (>=, <)
- Isso permite que o pip escolha a versão mais recente compatível dentro do range especificado
- O limite superior `<3.0.0` garante que não sejam instaladas versões breaking changes (major version 3.x)
- A versão mínima 2.3.0 do pydantic-settings satisfaz os requisitos do docling

### 2. LLM Clients

**Antes:**
```
anthropic==0.9.0
openai==1.12.0
```

**Depois:**
```
anthropic>=0.9.0,<1.0.0
openai>=1.12.0,<2.0.0
```

**Explicação educativa:**
- Tornamos as versões mais flexíveis para evitar futuros conflitos
- Essas bibliotecas podem ter atualizações menores compatíveis que resolvem bugs
- O limite superior previne breaking changes de major versions

### 3. HTTPX

**Antes:**
```
httpx==0.26.0
```

**Depois:**
```
httpx>=0.26.0,<1.0.0
```

**Explicação educativa:**
- HTTPX é uma dependência compartilhada entre anthropic, openai e nosso código
- Permitir um range de versões dá ao resolvedor mais flexibilidade
- Evita conflitos quando diferentes bibliotecas exigem versões levemente diferentes do httpx

## Estratégia de Versionamento Aplicada

### Semantic Versioning (SemVer)

Utilizamos o padrão **Semantic Versioning** nas constraints:

- **MAJOR.MINOR.PATCH** (ex: 2.3.0)
  - **MAJOR**: Mudanças incompatíveis na API (breaking changes)
  - **MINOR**: Novas funcionalidades compatíveis com versões anteriores
  - **PATCH**: Correções de bugs compatíveis

### Estratégias de Constraint

1. **Versão Fixa** (`==2.1.0`):
   - Vantagem: Reprodutibilidade total
   - Desvantagem: Pode criar conflitos, não recebe patches de segurança
   - Uso: Quando há problemas conhecidos com versões mais recentes

2. **Range Flexível** (`>=2.3.0,<3.0.0`):
   - Vantagem: Compatibilidade, recebe patches e melhorias
   - Desvantagem: Menos previsível (embora minor versions devam ser compatíveis)
   - Uso: Para a maioria das dependências em desenvolvimento

3. **Range Mínimo** (`>=2.0.0`):
   - Vantagem: Máxima flexibilidade
   - Desvantagem: Pode instalar versões com breaking changes
   - Uso: Dependências estáveis com bom versionamento

## Verificação da Solução

Para verificar que o conflito foi resolvido, executamos:

```bash
pip install --dry-run -r requirements.txt
```

**Resultado:** Todas as dependências foram resolvidas com sucesso, incluindo:
- pydantic 2.12.3 (atualizado de 2.5.3)
- pydantic-settings 2.11.0 (atualizado de 2.1.0)
- docling 2.4.2 (mantido)
- docling-core 2.3.1 (mantido)
- docling-parse 2.0.3 (mantido)

## Como Instalar as Dependências

Agora você pode instalar as dependências normalmente:

```bash
# 1. Certifique-se de estar no diretório correto
cd /Users/jwcunha/Documents/repos/phd-datascience/visao-computacional/doc_services/

# 2. (Recomendado) Ative seu ambiente virtual
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Verifique a instalação
pip list | grep -E "(pydantic|docling)"
```

## Boas Práticas Aprendidas

1. **Evite fixar versões desnecessariamente**: Use ranges quando possível
2. **Entenda as dependências transitivas**: Uma biblioteca pode exigir versões específicas de suas dependências
3. **Mantenha um requirements.txt atualizado**: Revise periodicamente as versões
4. **Use pip-compile ou Poetry**: Para gerenciamento mais robusto de dependências em produção
5. **Teste instalação em ambiente limpo**: Use `pip install --dry-run` antes de commitar mudanças

## Arquivos de Lock (Recomendação Futura)

Para ambientes de produção, considere usar:

- **requirements-lock.txt**: Versões exatas instaladas (gerado com `pip freeze`)
- **Poetry** ou **Pipenv**: Gerenciam automaticamente lock files
- **Docker**: Garante ambiente idêntico em desenvolvimento e produção

## Referências

- [Semantic Versioning](https://semver.org/)
- [pip Dependency Resolution](https://pip.pypa.io/en/stable/topics/dependency-resolution/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Docling Documentation](https://github.com/DS4SD/docling)

---

**Data da correção:** 2025-10-25
**Versão do Python:** 3.12
**Ambiente:** macOS (Darwin 25.0.0)
