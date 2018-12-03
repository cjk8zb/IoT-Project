import {Injectable} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {environment} from '../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class APIService {

  constructor(private http: HttpClient) { }

  getWeather(): Promise<any> {
    return this.get('weather');
  }

  getTopics(): Promise<any> {
    return this.get('topics');
  }

  private get(endpoint): Promise<any> {
    return this.http.get(environment.apiUrl + endpoint).toPromise();
  }

}
