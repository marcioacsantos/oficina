/* =========================================================
   Gestão de Oficina — interações do lado do cliente
   Sem dependências de backend / base de dados.
   ========================================================= */
(function () {
  "use strict";

  /* ---------- Tema claro / escuro (persistido no browser) ---------- */
  var root = document.documentElement;
  var toggleBtn = document.getElementById("themeToggle");
  var saved = localStorage.getItem("oficina-theme");

  function applyTheme(theme) {
    root.setAttribute("data-theme", theme);
    if (toggleBtn) {
      var icon = toggleBtn.querySelector("i");
      if (icon) icon.className = theme === "dark" ? "fa-solid fa-sun" : "fa-solid fa-moon";
    }
  }

  if (saved) applyTheme(saved);

  if (toggleBtn) {
    toggleBtn.addEventListener("click", function () {
      var current = root.getAttribute("data-theme") === "dark" ? "dark" : "light";
      var next = current === "dark" ? "light" : "dark";
      applyTheme(next);
      localStorage.setItem("oficina-theme", next);
    });
  }

  /* ---------- Alertas: fecho automático ---------- */
  document.querySelectorAll(".alert").forEach(function (alertEl) {
    setTimeout(function () {
      if (window.bootstrap && bootstrap.Alert) {
        var instance = bootstrap.Alert.getOrCreateInstance(alertEl);
        instance.close();
      }
    }, 5000);
  });

  /* ---------- Botões: estado "a processar..." ao submeter formulários ---------- */
  document.querySelectorAll("form").forEach(function (form) {
    form.addEventListener("submit", function () {
      if (form.dataset.noSpinner === "true") return;
      var btn = form.querySelector('button[type="submit"], button:not([type])');
      if (btn && !btn.disabled) {
        btn.dataset.originalHtml = btn.innerHTML;
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span>A processar...';
      }
    });
  });

  /* ---------- Botão "voltar ao topo" ---------- */
  var backToTop = document.getElementById("backToTop");
  if (backToTop) {
    window.addEventListener("scroll", function () {
      backToTop.classList.toggle("show", window.scrollY > 400);
    });
    backToTop.addEventListener("click", function () {
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }

  /* ---------- Sidebar móvel: fechar ao navegar ---------- */
  var sidebarToggle = document.getElementById("sidebarToggle");
  if (sidebarToggle) {
    document.querySelectorAll(".sidebar-link").forEach(function (link) {
      link.addEventListener("click", function () {
        sidebarToggle.checked = false;
      });
    });
  }

  /* ---------- Filtro de estado na lista de equipamentos (client-side) ---------- */
  var filtroEstado = document.getElementById("filtroEstado");
  if (filtroEstado) {
    filtroEstado.addEventListener("change", function () {
      var valor = filtroEstado.value;
      document.querySelectorAll("#tabelaEquipamentos tbody tr[data-estado]").forEach(function (row) {
        row.style.display = (!valor || row.dataset.estado === valor) ? "" : "none";
      });
    });
  }

  /* ---------- Pesquisa de equipamentos em tempo real (AJAX, com debounce) ---------- */
  var pesquisaInput = document.getElementById("pesquisaEquipamentos");
  var corpoTabela = document.getElementById("corpoTabelaEquipamentos");
  if (pesquisaInput && corpoTabela) {
    var debounceTimer = null;
    var pedidoAtual = null;

    function pesquisarEquipamentos() {
      var termo = pesquisaInput.value.trim();

      // Mantém o URL sincronizado (permite recarregar/partilhar a pesquisa).
      var url = new URL(window.location.href);
      if (termo) {
        url.searchParams.set("q", termo);
      } else {
        url.searchParams.delete("q");
      }
      window.history.replaceState(null, "", url);

      if (pedidoAtual) pedidoAtual.abort();
      pedidoAtual = new AbortController();

      fetch(url.toString(), {
        headers: { "X-Requested-With": "XMLHttpRequest" },
        signal: pedidoAtual.signal,
      })
        .then(function (resp) { return resp.text(); })
        .then(function (html) {
          corpoTabela.innerHTML = html;
          // Reaplica o filtro de estado atualmente selecionado, se houver.
          if (filtroEstado && filtroEstado.value) {
            filtroEstado.dispatchEvent(new Event("change"));
          }
        })
        .catch(function (err) {
          if (err.name !== "AbortError") console.error("Erro na pesquisa de equipamentos:", err);
        });
    }

    pesquisaInput.addEventListener("input", function () {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(pesquisarEquipamentos, 300);
    });

    var formPesquisa = document.getElementById("formPesquisaEquipamentos");
    if (formPesquisa) {
      formPesquisa.addEventListener("submit", function (e) {
        e.preventDefault();
        clearTimeout(debounceTimer);
        pesquisarEquipamentos();
      });
    }
  }

  /* ---------- Ordenação de tabelas ao clicar no cabeçalho da coluna ---------- */
  document.querySelectorAll("table").forEach(function (table) {
    var headers = table.querySelectorAll("thead th.sortable");
    if (!headers.length) return;

    headers.forEach(function (th, index) {
      th.addEventListener("click", function () {
        var tbody = table.querySelector("tbody");
        if (!tbody) return;

        var atualAsc = th.classList.contains("sort-asc");
        var direcaoAsc = !atualAsc;

        // Limpa o estado visual de todos os cabeçalhos desta tabela.
        headers.forEach(function (h) {
          h.classList.remove("sort-asc", "sort-desc");
          var icon = h.querySelector(".sort-icon");
          if (icon) icon.className = "fa-solid fa-sort sort-icon";
        });
        th.classList.add(direcaoAsc ? "sort-asc" : "sort-desc");
        var thIcon = th.querySelector(".sort-icon");
        if (thIcon) thIcon.className = "fa-solid " + (direcaoAsc ? "fa-sort-up" : "fa-sort-down") + " sort-icon";

        var linhas = Array.prototype.slice.call(tbody.querySelectorAll("tr"));
        // Ignora a linha de "sem resultados" (não tem células suficientes).
        var linhasValidas = linhas.filter(function (row) {
          return row.children.length > index;
        });

        linhasValidas.sort(function (a, b) {
          var valorA = a.children[index].innerText.trim();
          var valorB = b.children[index].innerText.trim();
          var comparacao = valorA.localeCompare(valorB, "pt", { numeric: true, sensitivity: "base" });
          return direcaoAsc ? comparacao : -comparacao;
        });

        linhasValidas.forEach(function (row) { tbody.appendChild(row); });
      });
    });
  });
})();
