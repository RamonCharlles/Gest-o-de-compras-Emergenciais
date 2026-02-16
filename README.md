<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SGF PA GOLD - Gestão de Engenharia</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
    <style>
        :root { --pa-gold: #D4AF37; --pa-blue: #0A192F; --sidebar-bg: #fdfdfd; }
        body { font-family: 'Segoe UI', Arial, sans-serif; background: #2C3E50; margin: 0; display: flex; }
        
        /* Painel de Instruções (Guia) */
        .guide-panel { width: 320px; background: var(--sidebar-bg); height: 100vh; position: fixed; padding: 25px; box-sizing: border-box; overflow-y: auto; border-right: 6px solid var(--pa-gold); box-shadow: 5px 0 15px rgba(0,0,0,0.3); z-index: 10; }
        .guide-panel h2 { color: var(--pa-blue); font-size: 18px; border-bottom: 2px solid var(--pa-gold); padding-bottom: 8px; }
        .instruction { margin-bottom: 18px; font-size: 13px; color: #444; line-height: 1.5; }
        .instruction b { color: var(--pa-blue); display: block; text-transform: uppercase; font-size: 11px; }

        /* Área de Trabalho */
        .workspace { margin-left: 320px; padding: 40px; width: 100%; display: flex; flex-direction: column; align-items: center; }
        .report-paper { background: white; width: 210mm; padding: 15mm; box-sizing: border-box; border-top: 10px solid var(--pa-gold); min-height: 297mm; box-shadow: 0 0 30px rgba(0,0,0,0.4); }

        /* Cabeçalho Conforme Modelo */
        .header-table { width: 100%; border-bottom: 2px solid var(--pa-blue); margin-bottom: 20px; }
        .brand { font-size: 26px; font-weight: 900; color: var(--pa-blue); letter-spacing: -1px; }
        .title-area { text-align: center; }
        .title-area h1 { font-size: 16px; margin: 0; color: var(--pa-blue); text-transform: uppercase; }
        .title-area p { font-size: 9px; font-weight: bold; color: #777; margin: 4px 0; }

        /* Seções e Grades */
        .section-label { background: var(--pa-blue); color: var(--pa-gold); padding: 7px 12px; font-size: 11px; font-weight: bold; text-transform: uppercase; margin-top: 20px; }
        .grid-container { display: grid; grid-template-columns: repeat(4, 1fr); border: 1px solid #ddd; }
        .field-box { border: 0.5px solid #ddd; padding: 10px; }
        .w-2 { grid-column: span 2; }
        .w-4 { grid-column: span 4; }

        label { display: block; font-size: 8px; font-weight: 800; color: var(--pa-blue); text-transform: uppercase; margin-bottom: 5px; }
        input, select, textarea { width: 100%; border: none; font-size: 12px; background: #fafafa; padding: 6px; box-sizing: border-box; font-family: inherit; }
        textarea { min-height: 90px; resize: none; overflow: hidden; line-height: 1.5; }

        /* Múltiplas Imagens */
        .evidence-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 15px; }
        .photo-item { border: 1px solid #ddd; padding: 12px; page-break-inside: avoid; }
        .drop-zone { width: 100%; height: 200px; border: 2px dashed #bbb; display: flex; align-items: center; justify-content: center; cursor: pointer; background: #fff; overflow: hidden; position: relative; }
        .drop-zone img { max-width: 100%; max-height: 100%; object-fit: contain; }
        .drop-zone span { font-size: 10px; color: #aaa; font-weight: bold; text-align: center; }

        .btn-generate { background: var(--pa-blue); color: var(--pa-gold); border: none; padding: 16px; width: 100%; font-weight: 900; cursor: pointer; border-radius: 6px; font-size: 14px; transition: 0.3s; margin-top: 20px; }
        .btn-generate:hover { background: #152a4a; transform: scale(1.02); }

        /* Formatação de Texto para PDF (Prevenção de Cortes) */
        .pdf-output-text { font-size: 12px; white-space: pre-wrap; color: #000; display: block; min-height: 20px; line-height: 1.5; }
    </style>
</head>
<body>

<nav class="guide-panel">
    <h2>Guia de Preenchimento</h2>
    
    <div class="instruction">
        <b>1. Identificação Técnica</b>
        Preencha o TAG do equipamento (ex: JB-04) e a Ordem de Manutenção. O MTTR é calculado com base nas horas de indisponibilidade[cite: 6, 23, 53].
    </div>

    <div class="instruction">
        <b>2. Matriz de Severidade (S.E.P)</b>
        Defina o impacto em Segurança, Meio Ambiente e Produção. Atribua o custo estimado do reparo (peças + mão de obra)[cite: 7, 32, 58].
    </div>

    <div class="instruction">
        <b>3. Relato do Fenômeno</b>
        Seja específico. Descreva o que falhou, como falhou e as evidências físicas encontradas. O campo expande automaticamente enquanto você digita para evitar cortes no PDF[cite: 12, 36, 66].
    </div>

    <div class="instruction">
        <b>4. Causa Raiz (RCFA)</b>
        Utilize a técnica dos 5 Porquês para identificar a causa sistêmica e proponha um bloqueio de engenharia definitivo[cite: 39, 68].
    </div>

    <div class="instruction">
        <b>5. Evidências Visuais</b>
        Clique nos quadros brancos para carregar fotos. Adicione comentários técnicos para cada imagem.
    </div>

    <button class="btn-generate" onclick="createEngineeringPDF()">GERAR PDF DEFINITIVO</button>
</nav>

<main class="workspace">
    <div id="capture-area" class="report-paper">
        <table class="header-table">
            <tr>
                <td class="brand">PA GOLD</td>
                <td class="title-area">
                    <h1>Informe de Engenharia e Análise de Falha</h1>
                    <p>SISTEMA INTEGRADO DE GESTÃO DE ATIVOS - ISO 55001 / WCM</p>
                </td>
                <td style="text-align: right; font-size: 9px; font-weight: bold; color: var(--pa-blue);">DOC: ITF-ENG-2026<br>REV: 005</td>
            </tr>
        </table>

        <div class="section-label">01. Identificação de Ativo e Logística</div>
        <div class="grid-container">
            <div class="field-box w-2"><label>Ativo (TAG)</label><input type="text" id="tag_f" placeholder="Ex: JB-04"></div>
            <div class="field-box w-2"><label>Centro de Custo</label><input type="text" placeholder="Ex: OPER-MINA-01"></div>
            <div class="field-box"><label>Nº Ordem</label><input type="text"></div>
            <div class="field-box"><label>Data da Falha</label><input type="date" id="date_f"></div>
            <div class="field-box"><label>Início Reparo</label><input type="time"></div>
            <div class="field-box"><label>Término Reparo</label><input type="time"></div>
            <div class="field-box w-4"><label>MTTR Estimado (Total de Horas)</label><input type="number" step="0.1"></div>
        </div>

        <div class="section-label" style="background: #8B0000;">02. Classificação de Impacto e Severidade (S.E.P)</div>
        <div class="grid-container">
            <div class="field-box"><label>Segurança (S)</label><select><option>NULO</option><option>BAIXO</option><option>CRÍTICO</option></select></div>
            <div class="field-box"><label>Ambiente (E)</label><select><option>NULO</option><option>BAIXO</option><option>CRÍTICO</option></select></div>
            <div class="field-box"><label>Produção (P)</label><select><option>PARADA TOTAL</option><option>PARADA PARCIAL</option><option>REDUÇÃO RITMO</option></select></div>
            <div class="field-box"><label>Custo Estimado (R$)</label><input type="text" placeholder="0.000,00"></div>
        </div>

        <div class="section-label">03. Descrição do Fenómeno e Relato Técnico</div>
        <div class="w-4" style="border: 1px solid #ddd; padding: 5px;">
            <textarea id="rel_desc" placeholder="Descreva as evidências físicas e o modo de falha encontrado..." oninput="autoExpand(this)"></textarea>
        </div>

        <div class="section-label">04. Investigação de Causa Raiz e Bloqueio</div>
        <div class="w-4" style="border: 1px solid #ddd; padding: 5px;">
            <textarea id="rcfa_desc" placeholder="Análise dos 5 Porquês e Plano de Ação de Bloqueio..." oninput="autoExpand(this)"></textarea>
        </div>

        <div style="page-break-before: always; margin-top: 30px;"></div>

        <div class="section-label">05. Evidências Fotográficas Comentadas</div>
        <div class="evidence-grid">
            <div class="photo-item">
                <div class="drop-zone" onclick="document.getElementById('file1').click()">
                    <span id="label1">CLIQUE PARA ADICIONAR FOTO 01<br>(MODO DE FALHA)</span>
                    <img id="preview1">
                </div>
                <input type="file" id="file1" hidden onchange="handleImg(this, 'preview1', 'label1')">
                <label style="margin-top:10px;">Comentário Técnico 01</label>
                <textarea id="com1" oninput="autoExpand(this)"></textarea>
            </div>
            <div class="photo-item">
                <div class="drop-zone" onclick="document.getElementById('file2').click()">
                    <span id="label2">CLIQUE PARA ADICIONAR FOTO 02<br>(REPARO/BLOQUEIO)</span>
                    <img id="preview2">
                </div>
                <input type="file" id="file2" hidden onchange="handleImg(this, 'preview2', 'label2')">
                <label style="margin-top:10px;">Comentário Técnico 02</label>
                <textarea id="com2" oninput="autoExpand(this)"></textarea>
            </div>
        </div>

        <div style="display: flex; justify-content: space-around; margin-top: 60px; border-top: 1px solid #333; padding-top: 10px; font-size: 10px; font-weight: bold; text-align: center;">
            <div style="width: 200px;">Emitente / Técnico</div>
            <div style="width: 200px;">Supervisor de Área</div>
            <div style="width: 200px;">Gestão de Ativos</div>
        </div>
    </div>
</main>

<script>
    function autoExpand(field) {
        field.style.height = 'inherit';
        field.style.height = field.scrollHeight + 'px';
    }

    function handleImg(input, imgId, labelId) {
        if (input.files && input.files[0]) {
            const reader = new FileReader();
            reader.onload = (e) => {
                document.getElementById(imgId).src = e.target.result;
                document.getElementById(labelId).style.display = 'none';
            };
            reader.readAsDataURL(input.files[0]);
        }
    }

    async function createEngineeringPDF() {
        const original = document.getElementById('capture-area');
        const tag = document.getElementById('tag_f').value || 'SGF';
        const date = document.getElementById('date_f').value || 'DATA';
        
        // Clonagem para tratamento de texto estático (Prevenção de cortes)
        const clone = original.cloneNode(true);
        
        // Converte TEXTAREAS em DIVS de texto estático no clone
        clone.querySelectorAll('textarea').forEach(ta => {
            const val = document.getElementById(ta.id).value;
            const textDiv = document.createElement('div');
            textDiv.className = 'pdf-output-text';
            textDiv.innerText = val || "---";
            ta.parentNode.replaceChild(textDiv, ta);
        });

        // Converte INPUTS e SELECTS em SPANS no clone
        clone.querySelectorAll('input, select').forEach(inp => {
            const span = document.createElement('span');
            span.className = 'pdf-output-text';
            span.style.fontWeight = 'bold';
            span.innerText = inp.value || "---";
            inp.parentNode.replaceChild(span, inp);
        });

        const opt = {
            margin: [10, 10, 10, 10],
            filename: `PAGOLD_SGF_${tag}_${date}.pdf`,
            html2canvas: { scale: 2, useCORS: true, letterRendering: true },
            jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' },
            pagebreak: { mode: ['avoid-all', 'css', 'legacy'] }
        };

        // Gera o PDF a partir do clone processado
        html2pdf().set(opt).from(clone).save();
    }
</script>
</body>
</html>
