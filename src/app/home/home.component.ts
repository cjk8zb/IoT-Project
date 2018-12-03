import {Component, OnInit} from '@angular/core';
import * as cloud from 'd3-cloud';
import {APIService} from '../api.service';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent implements OnInit {
  time = 'day';
  // icon: SVGUseElement;
  // textTemplate: SVGTextElement;
  // container: SVGGElement;
  // wordCloud: any;

  constructor(private api: APIService) { }

  ngOnInit() {
    const svg = <any>document.getElementById('word-cloud') as SVGSVGElement;
    const container = <any>svg.getElementById('container') as SVGGElement;
    const textTemplate = <any>svg.getElementById('text-template') as SVGTextElement;
    const background = <any>svg.getElementById('icon') as SVGUseElement;
    textTemplate.remove();
    container.setAttribute('transform', 'translate(400, 240)');

    this.api.getTopics().then(words => {
      const wordCloud = cloud().size([800, 480])
        .words(words)
        .padding(5)
        .font('Impact')
        .fontSize(d => d.value)
        .rotate(0)
        .spiral('rectangular')
        .on('end', w => {
          w.forEach(d => {
            const text = <any>textTemplate.cloneNode() as SVGTextElement;
            text.innerHTML = d.text;
            text.style.fontSize = d.size + 'px';
            text.style.fontFamily = d.font;
            text.style.fill = mood(d.sentiment, this.time === 'night');
            text.style.stroke = this.time === 'night' ? 'black' : 'white';
            text.style.strokeWidth = '2px';
            text.style.strokeOpacity = '0.5';
            text.setAttribute('transform', `translate(${[d.x, d.y]}) rotate(${d.rotate})`);
            text.setAttribute('text-anchor', 'middle');
            container.appendChild(text);
          });
        });
      wordCloud.start();
    });

    this.api.getWeather().then(data => {
      const {weather: [{main, icon}], sys: {sunrise, sunset}} = data;
      const now = Date.now();
      this.time = now >= sunrise && now < sunset ? 'day' : 'night';
      background.href.baseVal = `#icon${icon}`;
    }).catch(error => console.error('error', error));
  }
}

function mood(sentiment: number, night: boolean): string {
  if (!sentiment) {
    return 'white';
  }

  const positive = [0, 0, 255];
  const negative = [255, 0, 0];

  const color = sentiment > 0 ? positive : negative;
  const factor = night ? 1 - Math.abs(sentiment) : Math.abs(sentiment);

  const mixed = night ? [
    Math.floor(color[0] + (255 - color[0]) * factor),
    Math.floor(color[1] + (255 - color[1]) * factor),
    Math.floor(color[2] + (255 - color[2]) * factor)
  ] : [
    Math.floor(color[0] * factor),
    Math.floor(color[1] * factor),
    Math.floor(color[2] * factor)
  ];

  return `rgb(${mixed})`;
}
