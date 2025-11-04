import { Component, Input, OnInit, OnDestroy, ViewEncapsulation } from '@angular/core';
import { CommonModule } from '@angular/common';
import { 
  IonHeader, 
  IonToolbar, 
  IonTitle, 
  IonButtons, 
  IonButton, 
  IonIcon,
  ModalController
} from '@ionic/angular/standalone';
import { Router } from '@angular/router';
import { addIcons } from 'ionicons';
import { menu } from 'ionicons/icons';
import { AuthService } from '../../services/auth';
import { Subscription } from 'rxjs';
import { UserMenuComponent } from '../user-menu/user-menu.component';

@Component({
  selector: 'app-toolbar',
  templateUrl: './app-toolbar.component.html',
  styleUrls: ['./app-toolbar.component.scss'],
  standalone: true,
  encapsulation: ViewEncapsulation.None,
  imports: [
    CommonModule,
    IonHeader,
    IonToolbar,
    IonTitle,
    IonButtons,
    IonButton,
    IonIcon
  ]
})
export class AppToolbarComponent implements OnInit, OnDestroy {
  @Input() title: string = 'تطبيق توفير';
  @Input() showSearch: boolean = true;
  @Input() showNotifications: boolean = false;
  @Input() showMenu: boolean = true;
  @Input() transparent: boolean = false;

  isLoggedIn: boolean = false;
  private authSubscription?: Subscription;

  constructor(
    private authService: AuthService,
    private router: Router,
    private modalCtrl: ModalController
  ) {
    addIcons({ menu });
  }

  ngOnInit() {
    this.authSubscription = this.authService.isLoggedIn().subscribe(isLoggedIn => {
      this.isLoggedIn = isLoggedIn || false;
    });
  }

  ngOnDestroy() {
    if (this.authSubscription) {
      this.authSubscription.unsubscribe();
    }
  }
  
  async openUserMenu(event: Event) {
    // إيقاف انتشار الحدث لمنع تداخل
    event.stopPropagation();
    
    const modal = await this.modalCtrl.create({
      component: UserMenuComponent,
      cssClass: 'user-menu-modal',
      canDismiss: true,
      showBackdrop: true,
      backdropDismiss: true,
      // إزالة presentingElement لإصلاح مشكلة scroll
    });
    
    await modal.present();
  }

  /**
   * تبديل إلى placeholder إذا فشل تحميل الشعار
   */
  onLogoError(event: Event) {
    const img = event.target as HTMLImageElement;
    img.src = 'assets/images/logo-placeholder.svg';
  }
}
