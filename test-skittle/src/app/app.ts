import { Component } from '@angular/core';
import {SkillTester} from './components/skill-tester/skill-tester';

@Component({
  selector: 'app-root',
  imports: [SkillTester],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  protected title = 'test-skittle';
}
