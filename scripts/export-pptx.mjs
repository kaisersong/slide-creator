#!/usr/bin/env node

import { readdir, mkdir, rm, access } from 'node:fs/promises';
import { resolve, join, basename } from 'node:path';
import puppeteer from 'puppeteer';
import PptxGenJS from 'pptxgenjs';

const SLIDE_WIDTH = 1280;
const SLIDE_HEIGHT = 720;
const DEFAULT_SCALE_FACTOR = 3;

function parseArgs() {
  const args = process.argv.slice(2);
  if (args.length < 1) {
    console.error('Usage: node export-pptx.mjs <presentation-html> [output-filename] [--scale N]');
    console.error('Example: node export-pptx.mjs ./my-deck.html deck --scale 3');
    console.error('');
    console.error('For single-file presentations (genppt default):');
    console.error('  The script will render each slide section from the HTML file.');
    process.exit(1);
  }

  let scaleFactor = DEFAULT_SCALE_FACTOR;
  const scaleIdx = args.indexOf('--scale');
  if (scaleIdx !== -1) {
    scaleFactor = parseInt(args[scaleIdx + 1]) || DEFAULT_SCALE_FACTOR;
    args.splice(scaleIdx, 2);
  }

  const presentationFile = resolve(args[0]);
  const outputName = args[1] || basename(presentationFile, '.html');
  return { presentationFile, outputName, scaleFactor };
}

async function renderSlides(presentationFile, tempDir, scaleFactor) {
  await mkdir(tempDir, { recursive: true });

  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
  });

  const imagePaths = [];

  try {
    const page = await browser.newPage();
    await page.setViewport({
      width: SLIDE_WIDTH,
      height: SLIDE_HEIGHT,
      deviceScaleFactor: scaleFactor,
    });

    await page.goto(`file://${presentationFile}`, {
      waitUntil: 'networkidle0',
      timeout: 30000,
    });

    // Wait for initial animations
    await new Promise(r => setTimeout(r, 1500));

    // Get all slides
    const slideCount = await page.evaluate(() => {
      const slides = document.querySelectorAll('.slide');
      return slides.length;
    });

    console.log(`  Found ${slideCount} slides`);

    for (let i = 0; i < slideCount; i++) {
      const imageFile = join(tempDir, `slide${i + 1}.png`);

      console.log(`  Rendering slide ${i + 1}/${slideCount}`);

      // Scroll to the slide
      await page.evaluate((index) => {
        const slides = document.querySelectorAll('.slide');
        if (slides[index]) {
          slides[index].scrollIntoView({ behavior: 'instant' });
        }
      }, i);

      // Wait for animations to settle
      await new Promise(r => setTimeout(r, 1200));

      // Screenshot the slide element
      const slideHandle = await page.evaluateHandle((index) => {
        return document.querySelectorAll('.slide')[index];
      }, i);

      const element = slideHandle.asElement();
      if (element) {
        await element.screenshot({ path: imageFile, type: 'png' });
      } else {
        await page.screenshot({
          path: imageFile,
          type: 'png',
          clip: { x: 0, y: 0, width: SLIDE_WIDTH, height: SLIDE_HEIGHT },
        });
      }

      imagePaths.push(imageFile);
    }
  } finally {
    await browser.close();
  }

  return imagePaths;
}

async function buildPptx(imagePaths, outputPath, title) {
  const pptx = new PptxGenJS();

  // Standard 16:9 widescreen layout (10" x 5.625")
  pptx.defineLayout({ name: 'CUSTOM_16_9', width: 10, height: 5.625 });
  pptx.layout = 'CUSTOM_16_9';
  pptx.title = title;

  for (const imagePath of imagePaths) {
    const slide = pptx.addSlide();
    slide.addImage({
      path: imagePath,
      x: 0,
      y: 0,
      w: '100%',
      h: '100%',
    });
  }

  await pptx.writeFile({ fileName: outputPath });
}

async function cleanup(tempDir) {
  try {
    await rm(tempDir, { recursive: true, force: true });
  } catch {
    // best-effort cleanup
  }
}

async function main() {
  const { presentationFile, outputName, scaleFactor } = parseArgs();
  const outputDir = resolve(presentationFile, '..');
  const tempDir = join(outputDir, '.export-temp');
  const outputFile = join(outputDir, `${outputName}.pptx`);

  console.log('Exporting presentation to PPTX...');
  console.log(`  Source: ${presentationFile}`);
  console.log(`  Output: ${outputFile}`);
  console.log(`  Scale:  ${scaleFactor}x`);

  try {
    console.log('\n[1/3] Opening presentation...');
    await access(presentationFile);

    console.log('\n[2/3] Rendering slides to images...');
    const imagePaths = await renderSlides(presentationFile, tempDir, scaleFactor);

    console.log('\n[3/3] Building PPTX file...');
    await buildPptx(imagePaths, outputFile, outputName);

    console.log(`\nDone! PPTX saved to: ${outputFile}`);
  } catch (error) {
    console.error(`\nExport failed: ${error.message}`);
    process.exit(1);
  } finally {
    await cleanup(tempDir);
  }
}

main();
