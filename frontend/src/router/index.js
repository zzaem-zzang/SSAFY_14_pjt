import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'
import DrugDetailView from '@/views/DrugDetailView.vue'
import PostListView from '@/views/PostListView.vue'
import PostDetailView from '@/views/PostDetailView.vue'
import PostCreateView from '@/views/PostCreateView.vue'
import PostEditView from '@/views/PostEditView.vue'
import LoginView from '@/views/LoginView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: HomeView },
    { path: '/posts', name: 'PostList', component: PostListView },
    { path: '/posts/create', name: 'PostCreate', component: PostCreateView },
    { path: '/posts/:id', name: 'PostDetail', component: PostDetailView },
    { path: '/posts/:id/edit', name: 'PostEdit', component: PostEditView },
    { path: '/drugs/:id', component: DrugDetailView },
    { path: '/login', name: 'Login', component: LoginView },
  ],
})

export default router
