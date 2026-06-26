import { Routes } from '@angular/router';
import {SkillTester} from './components/skill-tester/skill-tester';

export const routes: Routes = [
  {
    path: '', component: SkillTester,
  },
  {
    path: '**', redirectTo: '', pathMatch: 'full'
  }
];
