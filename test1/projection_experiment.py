#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
正投影与斜投影对比实验程序
适用于学生学习投影原理
"""

import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import math


class ProjectionExperiment:
    """投影实验主类"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("正投影与斜投影对比实验")
        self.root.geometry("1200x800")
        
        # 实验参数
        self.cube_size = 4.0  # 正方体边长
        self.projection_angle = 30.0  # 斜投影角度(度)
        self.projection_mode = "orthogonal"  # orthogonal或oblique
        self.elevation = 20  # 视角仰角
        self.azimuth = 45  # 视角方位角
        
        # 创建界面
        self.create_widgets()
        
        # 绘制初始图形
        self.update_plot()
    
    def create_widgets(self):
        """创建界面组件"""
        
        # 左侧控制面板
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.grid(row=0, column=0, sticky=tk.W+tk.E+tk.N+tk.S)
        
        # 标题
        title_label = ttk.Label(control_frame, text="正投影与斜投影对比实验", 
                                font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=10)
        
        # 投影模式选择
        ttk.Label(control_frame, text="投影模式:", font=("Arial", 12)).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.mode_var = tk.StringVar(value="orthogonal")
        mode_frame = ttk.Frame(control_frame)
        mode_frame.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        ttk.Radiobutton(mode_frame, text="正投影", variable=self.mode_var, 
                       value="orthogonal", command=self.on_mode_change).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(mode_frame, text="斜投影", variable=self.mode_var, 
                       value="oblique", command=self.on_mode_change).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(mode_frame, text="对比模式", variable=self.mode_var, 
                       value="both", command=self.on_mode_change).pack(side=tk.LEFT, padx=5)
        
        # 斜投影角度调节
        ttk.Label(control_frame, text="斜投影角度 (度):", font=("Arial", 12)).grid(row=3, column=0, sticky=tk.W, pady=5)
        self.angle_var = tk.DoubleVar(value=30.0)
        angle_scale = ttk.Scale(control_frame, from_=0, to=60, variable=self.angle_var, 
                               orient=tk.HORIZONTAL, command=self.on_angle_change)
        angle_scale.grid(row=4, column=0, columnspan=2, sticky=tk.W+tk.E, pady=5)
        
        self.angle_label = ttk.Label(control_frame, text=f"{self.angle_var.get():.1f}°")
        self.angle_label.grid(row=5, column=0, columnspan=2, pady=5)
        
        # 视角控制
        ttk.Label(control_frame, text="视角控制:", font=("Arial", 12, "bold")).grid(row=6, column=0, sticky=tk.W, pady=(20, 5))
        
        ttk.Label(control_frame, text="仰角:").grid(row=7, column=0, sticky=tk.W, pady=5)
        self.elev_var = tk.DoubleVar(value=20)
        elev_scale = ttk.Scale(control_frame, from_=0, to=90, variable=self.elev_var, 
                              orient=tk.HORIZONTAL, command=self.on_view_change)
        elev_scale.grid(row=8, column=0, columnspan=2, sticky=tk.W+tk.E, pady=5)
        
        ttk.Label(control_frame, text="方位角:").grid(row=9, column=0, sticky=tk.W, pady=5)
        self.azim_var = tk.DoubleVar(value=45)
        azim_scale = ttk.Scale(control_frame, from_=0, to=360, variable=self.azim_var, 
                              orient=tk.HORIZONTAL, command=self.on_view_change)
        azim_scale.grid(row=10, column=0, columnspan=2, sticky=tk.W+tk.E, pady=5)
        
        # 测量数据显示
        ttk.Label(control_frame, text="测量数据:", font=("Arial", 12, "bold")).grid(row=11, column=0, sticky=tk.W, pady=(20, 5))
        
        self.data_text = tk.Text(control_frame, height=15, width=40, font=("Courier", 10))
        self.data_text.grid(row=12, column=0, columnspan=2, pady=5)
        
        # 按钮
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=13, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="刷新", command=self.update_plot).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="重置视角", command=self.reset_view).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="帮助", command=self.show_help).pack(side=tk.LEFT, padx=5)
        
        # 右侧绘图区域
        plot_frame = ttk.Frame(self.root)
        plot_frame.grid(row=0, column=1, sticky=tk.W+tk.E+tk.N+tk.S)
        
        # 创建matplotlib图形
        self.fig = Figure(figsize=(10, 8), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # 配置网格权重
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)
    
    def create_cube_vertices(self):
        """创建正方体顶点"""
        s = self.cube_size
        vertices = np.array([
            [0, 0, 0], [s, 0, 0], [s, s, 0], [0, s, 0],  # 底面
            [0, 0, s], [s, 0, s], [s, s, s], [0, s, s]   # 顶面
        ])
        return vertices
    
    def create_cube_faces(self, vertices):
        """创建正方体面"""
        faces = [
            [vertices[0], vertices[1], vertices[2], vertices[3]],  # 底面
            [vertices[4], vertices[5], vertices[6], vertices[7]],  # 顶面
            [vertices[0], vertices[1], vertices[5], vertices[4]],  # 前面
            [vertices[2], vertices[3], vertices[7], vertices[6]],  # 后面
            [vertices[0], vertices[3], vertices[7], vertices[4]],  # 左面
            [vertices[1], vertices[2], vertices[6], vertices[5]]   # 右面
        ]
        return faces
    
    def orthogonal_projection(self, point):
        """正投影: 垂直投影到xy平面"""
        return np.array([point[0], point[1], 0])
    
    def oblique_projection(self, point, angle_deg):
        """斜投影: 按角度投影到xy平面，只在x方向产生变形"""
        angle_rad = math.radians(angle_deg)
        k = math.tan(angle_rad)
        # 只在x方向产生变形，y方向保持垂直投影
        return np.array([point[0] + k * point[2], point[1], 0])
    
    def calculate_projection_length(self, vertices_proj):
        """计算投影边长"""
        # 计算底面四条边的长度
        edges = [
            np.linalg.norm(vertices_proj[1] - vertices_proj[0]),  # AB
            np.linalg.norm(vertices_proj[2] - vertices_proj[1]),  # BC
            np.linalg.norm(vertices_proj[3] - vertices_proj[2]),  # CD
            np.linalg.norm(vertices_proj[0] - vertices_proj[3])   # DA
        ]
        return edges
    
    def update_plot(self):
        """更新绘图"""
        self.fig.clear()
        
        mode = self.mode_var.get()
        
        if mode == "both":
            # 对比模式: 左右两个子图
            ax1 = self.fig.add_subplot(121, projection='3d')
            ax2 = self.fig.add_subplot(122, projection='3d')
            self.draw_projection(ax1, "orthogonal")
            self.draw_projection(ax2, "oblique")
            ax1.set_title("正投影", fontsize=14, fontweight='bold')
            ax2.set_title("斜投影", fontsize=14, fontweight='bold')
        else:
            # 单一模式
            ax = self.fig.add_subplot(111, projection='3d')
            self.draw_projection(ax, mode)
            title = "正投影" if mode == "orthogonal" else "斜投影"
            ax.set_title(title, fontsize=14, fontweight='bold')
        
        self.canvas.draw()
        self.update_measurement_data()
    
    def draw_projection(self, ax, mode):
        """绘制投影"""
        # 创建正方体
        vertices = self.create_cube_vertices()
        faces = self.create_cube_faces(vertices)
        
        # 绘制正方体
        cube = Poly3DCollection(faces, alpha=0.3, facecolor='cyan', edgecolor='blue', linewidth=2)
        ax.add_collection3d(cube)
        
        # 绘制正方体顶点
        ax.scatter(vertices[:, 0], vertices[:, 1], vertices[:, 2], 
                  color='blue', s=50, alpha=0.8)
        
        # 绘制投影面(xy平面)
        xx, yy = np.meshgrid(range(-1, int(self.cube_size)+2), range(-1, int(self.cube_size)+2))
        zz = np.zeros_like(xx)
        ax.plot_surface(xx, yy, zz, alpha=0.2, color='lightgray')
        
        # 计算投影点
        if mode == "orthogonal":
            vertices_proj = np.array([self.orthogonal_projection(v) for v in vertices])
            line_color = 'red'
            face_color = 'lightcoral'  # 正投影面颜色
        else:
            angle = self.angle_var.get()
            vertices_proj = np.array([self.oblique_projection(v, angle) for v in vertices])
            line_color = 'green'
            face_color = 'lightgreen'  # 斜投影面颜色
        
        # 绘制投射线
        for i, (v, vp) in enumerate(zip(vertices, vertices_proj)):
            ax.plot([v[0], vp[0]], [v[1], vp[1]], [v[2], vp[2]], 
                   color=line_color, linewidth=1.5, alpha=0.7)
        
        # 绘制投影点
        ax.scatter(vertices_proj[:, 0], vertices_proj[:, 1], vertices_proj[:, 2], 
                  color=line_color, s=50, alpha=0.8)
        
        # 绘制投影图形(底面四个点的投影)
        proj_bottom = vertices_proj[:4]
        
        # 绘制投影的边框，使其更加明显
        for i in range(4):
            j = (i + 1) % 4
            ax.plot([proj_bottom[i, 0], proj_bottom[j, 0]], 
                   [proj_bottom[i, 1], proj_bottom[j, 1]], 
                   [proj_bottom[i, 2], proj_bottom[j, 2]], 
                   color=line_color, linewidth=3, alpha=0.9)
        
        # 绘制投影面 - 连接四个投影点形成投影面
        # 创建投影面的四个顶点（按顺序连接）
        proj_face_vertices = [
            proj_bottom[0],  # 第一个投影点
            proj_bottom[1],  # 第二个投影点  
            proj_bottom[2],  # 第三个投影点
            proj_bottom[3]   # 第四个投影点
        ]
        
        # 使用Poly3DCollection绘制填充的投影面
        proj_faces = [proj_face_vertices]
        proj_surface = Poly3DCollection(proj_faces, alpha=0.4, facecolor=face_color, edgecolor=line_color, linewidth=3)
        ax.add_collection3d(proj_surface)
        
        # 额外绘制投影面的对角线，更清楚地显示投影面的形状
        if mode == "oblique":
            # 绘制对角线以更好地显示斜投影面的形状
            ax.plot([proj_bottom[0, 0], proj_bottom[2, 0]], 
                   [proj_bottom[0, 1], proj_bottom[2, 1]], 
                   [proj_bottom[0, 2], proj_bottom[2, 2]], 
                   color=line_color, linewidth=1, alpha=0.5, linestyle='--')
            ax.plot([proj_bottom[1, 0], proj_bottom[3, 0]], 
                   [proj_bottom[1, 1], proj_bottom[3, 1]], 
                   [proj_bottom[1, 2], proj_bottom[3, 2]], 
                   color=line_color, linewidth=1, alpha=0.5, linestyle='--')
        
        # 绘制完整的投影面（包括顶面投影）
        # 对于斜投影，需要绘制完整的投影体，而不仅仅是底面
        if mode == "oblique":
            # 绘制顶面投影
            proj_top = vertices_proj[4:]
            for i in range(4):
                j = (i + 1) % 4
                ax.plot([proj_top[i, 0], proj_top[j, 0]], 
                       [proj_top[i, 1], proj_top[j, 1]], 
                       [proj_top[i, 2], proj_top[j, 2]], 
                       color=line_color, linewidth=2, alpha=0.7)
            
            # 绘制侧面投影线
            for i in range(4):
                ax.plot([proj_bottom[i, 0], proj_top[i, 0]], 
                       [proj_bottom[i, 1], proj_top[i, 1]], 
                       [proj_bottom[i, 2], proj_top[i, 2]], 
                       color=line_color, linewidth=2, alpha=0.7)
            
            # 绘制完整的投影体面
            proj_faces = [
                [proj_bottom[0], proj_bottom[1], proj_bottom[2], proj_bottom[3]],  # 底面
                [proj_top[0], proj_top[1], proj_top[2], proj_top[3]],  # 顶面
                [proj_bottom[0], proj_bottom[1], proj_top[1], proj_top[0]],  # 前面
                [proj_bottom[2], proj_bottom[3], proj_top[3], proj_top[2]],  # 后面
                [proj_bottom[0], proj_bottom[3], proj_top[3], proj_top[0]],  # 左面
                [proj_bottom[1], proj_bottom[2], proj_top[2], proj_top[1]]   # 右面
            ]
            
            proj_body = Poly3DCollection(proj_faces, alpha=0.2, facecolor=face_color, edgecolor=line_color, linewidth=1)
            ax.add_collection3d(proj_body)
        
        # 对于正投影，也绘制完整的投影体
        elif mode == "orthogonal":
            # 绘制顶面投影（正投影的顶面投影与底面重合）
            proj_top = vertices_proj[4:]
            for i in range(4):
                j = (i + 1) % 4
                ax.plot([proj_top[i, 0], proj_top[j, 0]], 
                       [proj_top[i, 1], proj_top[j, 1]], 
                       [proj_top[i, 2], proj_top[j, 2]], 
                       color=line_color, linewidth=2, alpha=0.7)
            
            # 绘制侧面投影线（正投影的侧面投影为垂直线）
            for i in range(4):
                ax.plot([proj_bottom[i, 0], proj_top[i, 0]], 
                       [proj_bottom[i, 1], proj_top[i, 1]], 
                       [proj_bottom[i, 2], proj_top[i, 2]], 
                       color=line_color, linewidth=2, alpha=0.7)
            
            # 绘制完整的投影体面
            proj_faces = [
                [proj_bottom[0], proj_bottom[1], proj_bottom[2], proj_bottom[3]],  # 底面
                [proj_top[0], proj_top[1], proj_top[2], proj_top[3]],  # 顶面
                [proj_bottom[0], proj_bottom[1], proj_top[1], proj_top[0]],  # 前面
                [proj_bottom[2], proj_bottom[3], proj_top[3], proj_top[2]],  # 后面
                [proj_bottom[0], proj_bottom[3], proj_top[3], proj_top[0]],  # 左面
                [proj_bottom[1], proj_bottom[2], proj_top[2], proj_top[1]]   # 右面
            ]
            
            proj_body = Poly3DCollection(proj_faces, alpha=0.2, facecolor=face_color, edgecolor=line_color, linewidth=1)
            ax.add_collection3d(proj_body)
        
        # 设置坐标轴
        ax.set_xlabel('X (cm)', fontsize=10)
        ax.set_ylabel('Y (cm)', fontsize=10)
        ax.set_zlabel('Z (cm)', fontsize=10)
        
        # 设置视角
        ax.view_init(elev=self.elev_var.get(), azim=self.azim_var.get())
        
        # 设置坐标轴范围 - 扩大范围以适应斜投影
        # 计算斜投影的最大可能范围
        max_angle = 60  # 最大角度
        max_projection_extension = self.cube_size * math.tan(math.radians(max_angle))
        max_range = self.cube_size + max_projection_extension + 2  # 额外留出空间
        
        ax.set_xlim([-2, max_range])
        ax.set_ylim([-2, max_range])
        ax.set_zlim([-1, self.cube_size + 2])
        
        # 设置纵横比
        ax.set_box_aspect([1, 1, 0.8])
    
    def update_measurement_data(self):
        """更新测量数据"""
        self.data_text.delete(1.0, tk.END)
        
        vertices = self.create_cube_vertices()
        
        # 正投影数据
        vertices_ortho = np.array([self.orthogonal_projection(v) for v in vertices])
        edges_ortho = self.calculate_projection_length(vertices_ortho)
        
        # 斜投影数据
        angle = self.angle_var.get()
        vertices_oblique = np.array([self.oblique_projection(v, angle) for v in vertices])
        edges_oblique = self.calculate_projection_length(vertices_oblique)
        
        # 显示数据
        data = "=" * 35 + "\n"
        data += "正方体原始尺寸\n"
        data += "=" * 35 + "\n"
        data += f"边长: {self.cube_size:.2f} cm\n"
        data += f"体积: {self.cube_size**3:.2f} cm³\n\n"
        
        data += "=" * 35 + "\n"
        data += "正投影测量数据\n"
        data += "=" * 35 + "\n"
        edge_names = ["AB", "BC", "CD", "DA"]
        for name, length in zip(edge_names, edges_ortho):
            ratio = (length / self.cube_size) * 100
            data += f"{name}边: {length:.2f} cm ({ratio:.1f}%)\n"
        data += f"平均长度: {np.mean(edges_ortho):.2f} cm\n\n"
        
        data += "=" * 35 + "\n"
        data += f"斜投影测量数据 (角度: {angle:.1f}°)\n"
        data += "=" * 35 + "\n"
        for name, length in zip(edge_names, edges_oblique):
            ratio = (length / self.cube_size) * 100
            data += f"{name}边: {length:.2f} cm ({ratio:.1f}%)\n"
        data += f"平均长度: {np.mean(edges_oblique):.2f} cm\n\n"
        
        # 理论变形系数
        theoretical_ratio = 1 / math.cos(math.radians(angle)) if angle > 0 else 1.0
        data += "=" * 35 + "\n"
        data += "理论分析\n"
        data += "=" * 35 + "\n"
        data += f"理论变形系数: {theoretical_ratio:.4f}\n"
        data += f"实际变形系数: {np.mean(edges_oblique)/self.cube_size:.4f}\n"
        data += f"误差: {abs(theoretical_ratio - np.mean(edges_oblique)/self.cube_size):.4f}\n"
        
        self.data_text.insert(1.0, data)
    
    def on_mode_change(self):
        """投影模式改变"""
        self.update_plot()
    
    def on_angle_change(self, value):
        """角度改变"""
        self.angle_label.config(text=f"{self.angle_var.get():.1f}°")
        if self.mode_var.get() in ["oblique", "both"]:
            self.update_plot()
    
    def on_view_change(self, value):
        """视角改变"""
        self.update_plot()
    
    def reset_view(self):
        """重置视角"""
        self.elev_var.set(20)
        self.azim_var.set(45)
        self.update_plot()
    
    def show_help(self):
        """显示帮助信息"""
        help_text = """
正投影与斜投影对比实验程序

【实验目的】
1. 理解正投影和斜投影的基本概念
2. 掌握两种投影方式的特点和区别
3. 观察不同投影方式下物体形状的变化规律

【使用说明】
1. 选择投影模式: 正投影、斜投影或对比模式
2. 调节斜投影角度滑块,观察投影变化
3. 调节视角滑块,从不同角度观察
4. 查看右侧测量数据,分析投影特性

【投影原理】
• 正投影: 投射线垂直于投影面
  - 投影真实反映物体尺寸
  - 适用于工程制图

• 斜投影: 投射线与投影面成一定角度
  - 投影产生变形,变形系数 = 1/cos(θ)
  - 适用于艺术表现

【开发者】
实验教学辅助程序
版本: 1.0
        """
        messagebox.showinfo("帮助", help_text)


def main():
    """主函数"""
    root = tk.Tk()
    app = ProjectionExperiment(root)
    root.mainloop()


if __name__ == "__main__":
    main()
