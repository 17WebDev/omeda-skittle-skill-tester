import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import {SkillTester} from './components/skill-tester/skill-tester';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, SkillTester],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  protected title = 'test-skittle';
}
