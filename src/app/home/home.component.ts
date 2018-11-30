import {Component, OnInit} from '@angular/core';
import * as cloud from 'd3-cloud';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent implements OnInit {

  topics = [
    '#UMKC',
    'Chiefs',
    'Kansas City',
    'CS5590',
    '#Sports!!',
    'Finals Week',
    'Basketball',
    'Snow Day',
    '#ForkKnife',
    '#Fortnite'
  ];

  constructor() { }

  ngOnInit() {
    const words = this.topics.map(d => ({text: d, value: 10 + Math.random() * 90, sentiment: 1 - Math.random() * 2}));

    cloud().size([800, 480])
      .words(words)
      .padding(5)
      .font('Impact')
      .fontSize(d => d.value)
      .rotate(0)
      .spiral('rectangular')
      .on('end', w => {
        const svg = <any>document.getElementById('word-cloud') as SVGSVGElement;
        const container = <any>svg.getElementById('container') as SVGGElement;
        const textTemplate = <any>svg.getElementById('text-template') as SVGTextElement;
        textTemplate.remove();
        container.setAttribute('transform', 'translate(400, 240)');
        w.forEach(d => {
          console.log('word', d);
          const text = <any>textTemplate.cloneNode() as SVGTextElement;
          text.innerHTML = d.text;
          text.style.fontSize = d.size + 'px';
          text.style.fontFamily = d.font;
          text.style.fill = mood(d.sentiment);
          text.setAttribute('transform', `translate(${[d.x, d.y]}) rotate(${d.rotate})`);
          text.setAttribute('text-anchor', 'middle');
          container.appendChild(text);
        });
      })
      .start();


  }

}

function mood(sentiment: number): string {
  if (!sentiment) {
    return 'white';
  }

  const positive = [0, 0, 255];
  const negative = [255, 255, 0];

  const color = sentiment > 0 ? positive : negative;
  const white = 1 - Math.abs(sentiment);

  const mixed = [
    Math.floor(color[0] + (255 - color[0]) * white),
    Math.floor(color[1] + (255 - color[1]) * white),
    Math.floor(color[2] + (255 - color[2]) * white)
  ];

  return `rgb(${mixed})`;
}
