export type NotificationType='success'|'achievement'|'coins'|'xp'|'shield'|'info'|'error'|'update';
export type AppNotification={notificationId:string,type:NotificationType,title:string,message:string,createdAt:string,dismissAfterMs:number,dismissible:boolean,actionLabel?:string};
export class NotificationQueue{
 private items:AppNotification[]=[];
 private listeners=new Set<()=>void>();
 subscribe(listener:()=>void){this.listeners.add(listener);return()=>this.listeners.delete(listener)}
 snapshot(){return [...this.items]}
 current(){return this.items[0]||null}
 enqueue(input:Omit<AppNotification,'notificationId'|'createdAt'>){const item:AppNotification={...input,notificationId:crypto.randomUUID(),createdAt:new Date().toISOString()};this.items.push(item);this.emit();return item}
 dismiss(notificationId?:string){if(!this.items.length)return;this.items=notificationId?this.items.filter(x=>x.notificationId!==notificationId):this.items.slice(1);this.emit()}
 clear(){this.items=[];this.emit()}
 private emit(){for(const listener of this.listeners)listener()}
}
