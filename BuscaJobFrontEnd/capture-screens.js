
import puppeteer from 'puppeteer';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

(async () => {
  console.log('Iniciando captura de screenshots...');
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  const page = await browser.newPage();
  
  // Ajusta viewport para Full HD
  await page.setViewport({width: 1920, height: 1080});

  try {
    console.log('Acessando http://localhost:5173...');
    await page.goto('http://localhost:5173', {waitUntil: 'networkidle0', timeout: 30000});
    
    // Screenshot da Home
    console.log('Capturando Home...');
    await page.screenshot({path: path.resolve(__dirname, '../docs/screenshots/01-home.png')});

    // Screenshot focado nos filtros (Sidebar)
    console.log('Capturando Filtros...');
    // Vamos tentar pegar o elemento aside se possível, ou apenas um crop
    const sidebar = await page.$('aside');
    if (sidebar) {
        await sidebar.screenshot({path: path.resolve(__dirname, '../docs/screenshots/02-filtros.png')});
    } else {
        // Fallback: crop da esquerda
        await page.screenshot({
            path: path.resolve(__dirname, '../docs/screenshots/02-filtros.png'),
            clip: { x: 0, y: 0, width: 400, height: 800 }
        });
    }

    // Screenshot do botão de Reset (Highlight)
    // Tenta focar ou hover no botão de reset se possível
    // Mas por simplicidade, vamos pular ou fazer um full page
    
    console.log('Capturas concluídas com sucesso!');

  } catch (error) {
    console.error('Erro ao capturar screenshots:', error);
  } finally {
    await browser.close();
  }
})();
