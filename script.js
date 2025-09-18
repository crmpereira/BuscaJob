class BuscaJobApp {
    constructor() {
        this.currentJobs = [];
        this.stats = {
            totalBuscas: 0,
            totalVagas: 0,
            vagasSalvas: 0
        };
        
        this.init();
        this.loadStats();
        this.modal = null;
    }

    init() {
        this.setupFormValidation();
        this.carregarConfiguracao();
        this.displayStats();
        this.setupModal();
        
        // Event listeners
        document.getElementById('buscar-agora').addEventListener('click', () => this.buscarVagas());
        document.getElementById('salvar-config').addEventListener('click', () => this.salvarConfiguracao());
        
        // Enter key support
        document.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && e.target.closest('.search-form')) {
                this.buscarVagas();
            }
        });
    }

    setupFormValidation() {
        const form = document.getElementById('job-search-form');
        const inputs = form.querySelectorAll('input[required]');
        
        inputs.forEach(input => {
            input.addEventListener('blur', () => this.validateField(input));
            input.addEventListener('input', () => this.clearFieldError(input));
        });
    }

    validateField(field) {
        const value = field.value.trim();
        const fieldName = field.getAttribute('name');
        
        // Remove existing error
        this.clearFieldError(field);
        
        if (field.hasAttribute('required') && !value) {
            this.showFieldError(field, 'Este campo é obrigatório');
            return false;
        }
        
        return true;
    }

    showFieldError(field, message) {
        field.classList.add('error');
        
        let errorDiv = field.parentNode.querySelector('.error-message');
        if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.className = 'error-message';
            field.parentNode.appendChild(errorDiv);
        }
        
        errorDiv.textContent = message;
    }

    clearFieldError(field) {
        field.classList.remove('error');
        const errorDiv = field.parentNode.querySelector('.error-message');
        if (errorDiv) {
            errorDiv.remove();
        }
    }

    async buscarVagas() {
        const formData = this.getFormData();
        
        if (!this.validateForm(formData)) {
            this.showNotification('Por favor, preencha os campos obrigatórios', 'error');
            return;
        }

        this.showLoading(true);
        this.clearResults();

        try {
            // Simulate API call - replace with actual backend call
            const response = await this.simulateJobSearch(formData);
            
            this.displayResults(response.vagas);
            this.updateStats('totalBuscas', this.stats.totalBuscas + 1);
            this.updateStats('totalVagas', this.stats.totalVagas + response.vagas.length);
            
            this.showNotification(`Encontradas ${response.vagas.length} vagas!`, 'success');
            
        } catch (error) {
            console.error('Erro na busca:', error);
            this.showNotification('Erro ao buscar vagas. Tente novamente.', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    coletarDadosFormulario() {
        const cargo = document.getElementById('cargo').value.trim();
        const localizacao = document.getElementById('localizacao').value.trim();
        const salarioMin = document.getElementById('salario-min').value;
        const salarioMax = document.getElementById('salario-max').value;
        const nivel = document.getElementById('nivel').value;
        const palavrasChave = document.getElementById('palavras-chave').value.trim();
        const frequencia = document.getElementById('frequencia').value;
        
        // Coletar sites selecionados
        const sitesCheckboxes = document.querySelectorAll('input[name="sites"]:checked');
        const sites = Array.from(sitesCheckboxes).map(cb => cb.value);
        
        // Coletar tipos de contratação selecionados
        const tiposCheckboxes = document.querySelectorAll('input[name="tipo-contratacao"]:checked');
        const tiposContratacao = Array.from(tiposCheckboxes).map(cb => cb.value);

        return {
            cargo,
            localizacao,
            salario_minimo: salarioMin ? parseInt(salarioMin) : null,
            salario_maximo: salarioMax ? parseInt(salarioMax) : null,
            nivel,
            palavras_chave: palavrasChave,
            sites,
            tipos_contratacao: tiposContratacao,
            frequencia
        };
    }

    getFormData() {
        return this.coletarDadosFormulario();
    }

    validateForm(data) {
        const erros = this.validarFormulario(data);
        
        if (erros.length > 0) {
            erros.forEach(erro => {
                this.showNotification(erro, 'error');
            });
            return false;
        }
        
        return true;
    }

    validarFormulario(dados) {
        const erros = [];

        if (!dados.cargo) {
            erros.push('Cargo é obrigatório');
        }

        if (!dados.localizacao) {
            erros.push('Localização é obrigatória');
        }

        if (!dados.sites || dados.sites.length === 0) {
            erros.push('Selecione pelo menos um site');
        }

        if (!dados.tipos_contratacao || dados.tipos_contratacao.length === 0) {
            erros.push('Selecione pelo menos um tipo de contratação');
        }

        // Validar range salarial
        if (dados.salario_minimo && dados.salario_maximo) {
            if (dados.salario_minimo > dados.salario_maximo) {
                erros.push('Salário mínimo não pode ser maior que o máximo');
            }
        }

        if (dados.salario_minimo && dados.salario_minimo < 0) {
            erros.push('Salário mínimo deve ser positivo');
        }

        if (dados.salario_maximo && dados.salario_maximo < 0) {
            erros.push('Salário máximo deve ser positivo');
        }

        return erros;
    }

    async simulateJobSearch(criteria) {
        try {
            // Chama API Python real
            const response = await fetch('/api/buscar-vagas', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(criteria)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.error || 'Erro desconhecido na API');
            }
            
            return data;
            
        } catch (error) {
            console.error('Erro na API:', error);
            
            // Fallback para dados mock se API falhar
            console.log('Usando dados mock como fallback...');
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            const mockJobs = this.generateMockJobs(criteria);
            
            return {
                success: true,
                vagas: mockJobs,
                total: mockJobs.length
            };
        }
    }

    generateMockJobs(criteria) {
        const companies = ['TechCorp', 'InnovaSoft', 'DataSolutions', 'CloudTech', 'StartupXYZ', 'MegaCorp', 'EduTech'];
        const cities = [
            'São Paulo', 'Rio de Janeiro', 'Belo Horizonte', 'Porto Alegre', 'Curitiba', 
            'Salvador', 'Brasília', 'Fortaleza', 'Recife', 'Goiânia', 'Florianópolis', 
            'Campinas', 'Santos', 'Ribeirão Preto', 'Sorocaba', 'Joinville', 'Londrina'
        ];
        const states = ['SP', 'RJ', 'MG', 'RS', 'PR', 'BA', 'DF', 'CE', 'PE', 'GO', 'SC'];
        const jobTypes = ['CLT', 'PJ', 'Freelancer', 'Estágio'];
        const sites = ['linkedin', 'indeed', 'catho', 'vagas', 'glassdoor', 'infojobs', 'stackoverflow', 'github', 'trampos', 'rocket', 'startup'];
        
        let jobs = [];
        const numJobs = Math.floor(Math.random() * 15) + 5; // 5-20 jobs
        
        for (let i = 0; i < numJobs; i++) {
            const company = companies[Math.floor(Math.random() * companies.length)];
            
            // Generate more specific location data
            let location;
            if (Math.random() < 0.15) { // 15% chance for remote
                location = 'Remoto';
            } else {
                const city = cities[Math.floor(Math.random() * cities.length)];
                const state = states[Math.floor(Math.random() * states.length)];
                location = `${city}, ${state}`;
            }
            
            const jobType = jobTypes[Math.floor(Math.random() * jobTypes.length)];
            const selectedSite = sites[Math.floor(Math.random() * sites.length)];
            let salary;
            
            // Adjust salary based on job type and site
            if (jobType === 'Estágio') {
                salary = Math.floor(Math.random() * 800) + 800; // 800-1600
            } else if (jobType === 'Freelancer') {
                salary = Math.floor(Math.random() * 100) + 50; // 50-150 per hour
            } else {
                // Higher salaries for international sites
                if (['stackoverflow', 'github', 'rocket', 'startup'].includes(selectedSite)) {
                    salary = Math.floor(Math.random() * 12000) + 5000; // 5000-17000
                } else {
                    salary = Math.floor(Math.random() * 8000) + 2000; // 2000-10000
                }
            }
            
            const salaryText = jobType === 'Freelancer' ? 
                `R$ ${salary}/hora` : 
                `R$ ${salary.toLocaleString('pt-BR')}`;
            
            // Adjust job title based on site
            let jobTitle = `${criteria.cargo || 'Desenvolvedor'} - ${company}`;
            if (selectedSite === 'stackoverflow') {
                jobTitle = `Senior ${criteria.cargo || 'Developer'} - ${company}`;
            } else if (selectedSite === 'github') {
                jobTitle = `${criteria.cargo || 'Developer'} (Open Source) - ${company}`;
            } else if (selectedSite === 'startup') {
                jobTitle = `Founding ${criteria.cargo || 'Developer'} - ${company}`;
            } else if (selectedSite === 'rocket') {
                jobTitle = `Lead ${criteria.cargo || 'Developer'} - ${company}`;
            }
            
            jobs.push({
                id: `job_${Date.now()}_${i}`,
                titulo: jobTitle,
                empresa: company,
                localizacao: location,
                salario: salaryText,
                tipo: jobType,
                tipo_contratacao: jobType,
                descricao: `Vaga para ${criteria.cargo || 'profissional'} com experiência em tecnologias modernas. Oportunidade de crescimento em empresa inovadora.`,
                dataPublicacao: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toLocaleDateString('pt-BR'),
                site: selectedSite,
                nivel_experiencia: jobType === 'Estágio' ? 'Estágio' : ['Júnior', 'Pleno', 'Sênior'][Math.floor(Math.random() * 3)],
                palavras_chave: this.generateKeywords(criteria.cargo || 'Desenvolvedor'),
                url: '#'
            });
        }
        
        // Apply filters to mock data
        if (criteria.tipos_contratacao && criteria.tipos_contratacao.length > 0) {
            jobs = jobs.filter(job => 
                criteria.tipos_contratacao.includes(job.tipo_contratacao)
            );
        }
        
        // Filter by salary range (basic simulation)
        if (criteria.salario_minimo || criteria.salario_maximo) {
            jobs = jobs.filter(job => {
                // Extract numeric value from salary (simplified)
                const salaryMatch = job.salario.match(/R\$\s*([\d.,]+)/);
                if (salaryMatch) {
                    const jobSalary = parseInt(salaryMatch[1].replace(/[.,]/g, ''));
                    
                    if (criteria.salario_minimo && jobSalary < criteria.salario_minimo) {
                        return false;
                    }
                    if (criteria.salario_maximo && jobSalary > criteria.salario_maximo) {
                        return false;
                    }
                }
                return true;
            });
        }
        
        return jobs;
    }

    generateKeywords(cargo) {
        const keywordSets = {
            'Desenvolvedor': ['JavaScript', 'React', 'Node.js', 'Python', 'SQL', 'Git'],
            'Analista': ['Excel', 'Power BI', 'SQL', 'Python', 'Análise de Dados'],
            'Designer': ['Photoshop', 'Illustrator', 'Figma', 'UI/UX', 'Adobe Creative'],
            'Marketing': ['Google Ads', 'Facebook Ads', 'SEO', 'Analytics', 'Social Media'],
            'Vendas': ['CRM', 'Negociação', 'Prospecção', 'Relacionamento', 'Metas']
        };
        
        const defaultKeywords = ['Comunicação', 'Trabalho em Equipe', 'Proatividade'];
        const specificKeywords = keywordSets[cargo] || keywordSets['Desenvolvedor'];
        
        // Combinar palavras-chave específicas com algumas gerais
        const allKeywords = [...specificKeywords, ...defaultKeywords];
        
        // Retornar 3-5 palavras-chave aleatórias
        const numKeywords = Math.floor(Math.random() * 3) + 3;
        const shuffled = allKeywords.sort(() => 0.5 - Math.random());
        return shuffled.slice(0, numKeywords);
    }

    displayResults(vagas) {
        this.currentJobs = vagas; // Armazenar vagas atuais
        const container = document.getElementById('results-container');
        
        if (vagas.length === 0) {
            container.innerHTML = '<p class="no-results">Nenhuma vaga encontrada com os critérios especificados.</p>';
            return;
        }
        
        const html = vagas.map(vaga => this.createJobCard(vaga)).join('');
        container.innerHTML = html;
        
        // Add event listeners to job cards
        this.setupJobCardEvents();
    }

    createJobCard(vaga) {
        return `
            <div class="job-card fade-in" data-job-id="${vaga.id}">
                <div class="job-header">
                    <div class="job-title">${vaga.titulo}</div>
                    <div class="job-location-highlight">
                        <i class="fas fa-map-marker-alt location-icon"></i> 
                        <span class="location-text">${vaga.localizacao}</span>
                    </div>
                </div>
                <div class="job-company"><i class="fas fa-building"></i> ${vaga.empresa}</div>
                <div class="job-salary"><i class="fas fa-dollar-sign"></i> ${vaga.salario}</div>
                <div class="job-description">${vaga.descricao}</div>
                <div class="job-meta">
                    <small><i class="fas fa-calendar"></i> ${vaga.dataPublicacao} | <i class="fas fa-briefcase"></i> ${vaga.tipo_contratacao || vaga.tipo} | <i class="fas fa-globe"></i> ${vaga.site}</small>
                </div>
                <div class="job-actions">
                    <button class="btn btn-primary btn-small" onclick="app.salvarVaga('${vaga.id}')">
                        <i class="fas fa-heart"></i> Salvar
                    </button>
                    <button class="btn btn-secondary btn-small" onclick="app.verDetalhes('${vaga.id}')">
                        <i class="fas fa-eye"></i> Ver Detalhes
                    </button>
                    <a href="${vaga.url}" target="_blank" class="btn btn-secondary btn-small">
                        <i class="fas fa-external-link-alt"></i> Abrir no Site
                    </a>
                </div>
            </div>
        `;
    }

    setupJobCardEvents() {
        const jobCards = document.querySelectorAll('.job-card');
        jobCards.forEach(card => {
            card.addEventListener('mouseenter', () => {
                card.style.transform = 'translateY(-5px)';
            });
            
            card.addEventListener('mouseleave', () => {
                card.style.transform = 'translateY(0)';
            });
        });
    }

    salvarVaga(jobId) {
        // Get job data
        const jobCard = document.querySelector(`[data-job-id="${jobId}"]`);
        if (!jobCard) return;
        
        // Save to localStorage (in a real app, this would be sent to backend)
        let savedJobs = JSON.parse(localStorage.getItem('savedJobs') || '[]');
        
        // Check if already saved
        if (savedJobs.includes(jobId)) {
            this.showNotification('Vaga já foi salva anteriormente', 'info');
            return;
        }
        
        savedJobs.push(jobId);
        localStorage.setItem('savedJobs', JSON.stringify(savedJobs));
        
        this.updateStats('vagasSalvas', this.stats.vagasSalvas + 1);
        this.showNotification('Vaga salva com sucesso!', 'success');
        
        // Visual feedback
        const saveBtn = jobCard.querySelector('.btn-primary');
        const originalText = saveBtn.innerHTML;
        saveBtn.innerHTML = '<i class="fas fa-check"></i> Salva';
        saveBtn.classList.add('pulse');
        
        setTimeout(() => {
            saveBtn.innerHTML = originalText;
            saveBtn.classList.remove('pulse');
        }, 2000);
    }

    verDetalhes(jobId) {
        const vaga = this.currentJobs.find(job => job.id === jobId);
        if (!vaga) {
            this.showNotification('Vaga não encontrada', 'error');
            return;
        }
        
        this.openJobModal(vaga);
    }

    setupModal() {
        this.modal = document.getElementById('job-modal');
        
        // Event listeners para fechar modal
        const closeButtons = this.modal.querySelectorAll('.close-modal, .close-modal-btn');
        closeButtons.forEach(btn => {
            btn.addEventListener('click', () => this.closeJobModal());
        });
        
        // Fechar modal clicando no fundo
        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) {
                this.closeJobModal();
            }
        });
        
        // Fechar modal com ESC
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.modal.style.display === 'block') {
                this.closeJobModal();
            }
        });
    }

    openJobModal(vaga) {
        // Preencher dados do modal
        document.getElementById('modal-job-title').textContent = vaga.titulo || 'Título não disponível';
        document.getElementById('modal-company').textContent = vaga.empresa || 'Não informado';
        document.getElementById('modal-location').textContent = vaga.localizacao || 'Não informado';
        document.getElementById('modal-salary').textContent = vaga.salario || 'Não informado';
        document.getElementById('modal-contract-type').textContent = vaga.tipo_contratacao || vaga.tipo || 'Não informado';
        document.getElementById('modal-experience-level').textContent = vaga.nivel_experiencia || 'Não informado';
        document.getElementById('modal-publish-date').textContent = vaga.dataPublicacao || vaga.data_publicacao || 'Não informado';
        document.getElementById('modal-source-site').textContent = vaga.site || vaga.site_origem || 'Não informado';
        
        // Descrição
        const descriptionElement = document.getElementById('modal-description');
        if (vaga.descricao && vaga.descricao.trim()) {
            descriptionElement.innerHTML = `<p>${vaga.descricao}</p>`;
        } else {
            descriptionElement.innerHTML = '<p>Descrição não disponível</p>';
        }
        
        // Palavras-chave
        const keywordsContainer = document.getElementById('modal-keywords');
        if (vaga.palavras_chave && vaga.palavras_chave.length > 0) {
            const keywordTags = vaga.palavras_chave.map(keyword => 
                `<span class="keyword-tag">${keyword}</span>`
            ).join('');
            keywordsContainer.innerHTML = keywordTags;
        } else {
            keywordsContainer.innerHTML = '<span class="keyword-tag">Nenhuma palavra-chave disponível</span>';
        }
        
        // Link para candidatura
        const applyLink = document.getElementById('modal-apply-link');
        if (vaga.url) {
            applyLink.href = vaga.url;
            applyLink.style.display = 'inline-flex';
        } else {
            applyLink.style.display = 'none';
        }
        
        // Mostrar modal
        this.modal.style.display = 'block';
        document.body.style.overflow = 'hidden'; // Prevenir scroll da página
    }

    closeJobModal() {
        this.modal.style.display = 'none';
        document.body.style.overflow = 'auto'; // Restaurar scroll da página
    }

    salvarConfiguracao() {
        const formData = this.getFormData();
        
        // Salva localmente
        localStorage.setItem('jobSearchConfig', JSON.stringify(formData));
        
        // Salva no backend
        fetch('/api/salvar-configuracao', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.showNotification('Configuração salva com sucesso!', 'success');
            } else {
                this.showNotification('Erro ao salvar configuração no servidor', 'warning');
            }
        })
        .catch(error => {
            console.error('Erro ao salvar configuração:', error);
            this.showNotification('Configuração salva localmente', 'info');
        });
    }

    carregarConfiguracao() {
        const savedConfig = localStorage.getItem('jobSearchConfig');
        if (!savedConfig) return;
        
        try {
            const config = JSON.parse(savedConfig);
            const form = document.getElementById('job-search-form');
            
            // Fill form fields
            Object.keys(config).forEach(key => {
                if (key === 'sites') {
                    // Handle checkboxes
                    const checkboxes = form.querySelectorAll(`input[name="${key}"]`);
                    checkboxes.forEach(checkbox => {
                        checkbox.checked = config[key].includes(checkbox.value);
                    });
                } else {
                    const field = form.querySelector(`[name="${key}"]`);
                    if (field) {
                        field.value = config[key];
                    }
                }
            });
            
        } catch (error) {
            console.error('Erro ao carregar configuração:', error);
        }
    }

    showLoading(show) {
        const loading = document.getElementById('loading');
        if (show) {
            loading.classList.remove('hidden');
        } else {
            loading.classList.add('hidden');
        }
    }

    clearResults() {
        const container = document.getElementById('results-container');
        container.innerHTML = '<p class="no-results">Buscando vagas...</p>';
    }

    updateStats(statName, value) {
        this.stats[statName] = value;
        this.saveStats();
        this.displayStats();
    }

    loadStats() {
        const savedStats = localStorage.getItem('jobSearchStats');
        if (savedStats) {
            this.stats = { ...this.stats, ...JSON.parse(savedStats) };
        }
        this.displayStats();
    }

    saveStats() {
        localStorage.setItem('jobSearchStats', JSON.stringify(this.stats));
    }

    displayStats() {
        document.getElementById('total-buscas').textContent = this.stats.totalBuscas;
        document.getElementById('total-vagas').textContent = this.stats.totalVagas;
        document.getElementById('vagas-salvas').textContent = this.stats.vagasSalvas;
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <i class="fas fa-${this.getNotificationIcon(type)}"></i>
            <span>${message}</span>
            <button class="notification-close" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        // Add styles if not already added
        if (!document.querySelector('#notification-styles')) {
            const styles = document.createElement('style');
            styles.id = 'notification-styles';
            styles.textContent = `
                .notification {
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    padding: 15px 20px;
                    border-radius: 8px;
                    color: white;
                    display: flex;
                    align-items: center;
                    gap: 10px;
                    z-index: 1000;
                    animation: slideIn 0.3s ease;
                    max-width: 400px;
                    box-shadow: 0 5px 15px rgba(0,0,0,0.2);
                }
                
                .notification-success { background: #38a169; }
                .notification-error { background: #e53e3e; }
                .notification-info { background: #3182ce; }
                .notification-warning { background: #d69e2e; }
                
                .notification-close {
                    background: none;
                    border: none;
                    color: white;
                    cursor: pointer;
                    padding: 0;
                    margin-left: auto;
                }
                
                @keyframes slideIn {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
            `;
            document.head.appendChild(styles);
        }
        
        document.body.appendChild(notification);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }

    getNotificationIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            info: 'info-circle',
            warning: 'exclamation-triangle'
        };
        return icons[type] || 'info-circle';
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new BuscaJobApp();
});

// Add some utility functions
function formatCurrency(value) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(value);
}

function formatDate(date) {
    return new Intl.DateTimeFormat('pt-BR').format(new Date(date));
}

// Export for potential use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = BuscaJobApp;
}