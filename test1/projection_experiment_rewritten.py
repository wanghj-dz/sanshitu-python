#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
正投影与斜投影对比实验程序 - 完全重写版
基于修复总结报告重新编写，解决了所有已知问题
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
    """投影实验主类 - 完全重写版"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("正投影与斜投影对比实验 - 重写版")
        self.root.geometry("1400x900")
        
        # 实验参数
        self.cube_size = 4.0  # 正方体边长
        self.projection_angle = 30.0  # 斜投影角度(度)
        self.projection_mode = "orthogonal"  # orthogonal或oblique或both
        self.elevation = 20  # 视角仰角
        self.azimuth = 45  # 视角方位角
        
        # 创建界面
        self.create_widgets()
        
        # 绘制初始图形
        self.update_plot()
    
    def create_widgets(self):
        """创建界面组件"""
        # 主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 左侧控制面板
        control_frame = ttk.LabelFrame(main_frame, text="控制面板", padding="10")
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # 标题
        title_label = ttk.Label(control_frame, text="正投影与斜投影对比实验", 
                                font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # 投影模式选择
        mode_frame = ttk.LabelFrame(control_frame, text="投影模式", padding="10")
        mode_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.mode_var = tk.StringVar(value="orthogonal")
        ttk.Radiobutton(mode_frame, text="正投影", variable=self.mode_var, 
                       value="orthogonal", command=self.on_mode_change).pack(anchor=tk.W)
        ttk.Radiobutton(mode_frame, text="斜投影", variable=self.mode_var, 
                       value="oblique", command=self.on_mode_change).pack(anchor=tk.W)
        ttk.Radiobutton(mode_frame, text="对比模式", variable=self.mode_var, 
                       value="both", command=self.on_mode_change).pack(anchor=tk.W)
        
        # 参数调节
        param_frame = ttk.LabelFrame(control_frame, text="参数调节", padding="10")
        param_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 斜投影角度
        ttk.Label(param_frame, text="斜投影角度:").pack(anchor=tk.W)
        self.angle_var = tk.DoubleVar(value=30.0)
        angle_scale = ttk.Scale(param_frame, from_=0, to=60, variable=self.angle_var, 
                               orient=tk.HORIZONTAL, command=self.on_angle_change)
        angle_scale.pack(fill=tk.X, pady=(5, 0))
        self.angle_label = ttk.Label(param_frame, text=f"{self.angle_var.get():.1f}°")
        self.angle_label.pack()
        
        # 视角控制
        view_frame = ttk.LabelFrame(control_frame, text="视角控制", padding="10")
        view_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(view_frame, text="仰角:").pack(anchor=tk.W)
        self.elev_var = tk.DoubleVar(value=20)
        elev_scale = ttk.Scale(view_frame, from_=0, to=90, variable=self.elev_var, 
                              orient=tk.HORIZONTAL, command=self.on_view_change)
        elev_scale.pack(fill=tk.X, pady=(5, 10))
        
        ttk.Label(view_frame, text="方位角:").pack(anchor=tk.W)
        self.azim_var = tk.DoubleVar(value=45)
        azim_scale = ttk.Scale(view_frame, from_=0, to=360, variable=self.azim_var, 
                              orient=tk.HORIZONTAL, command=self.on_view_change)
        azim_scale.pack(fill=tk.X, pady=(5, 0))
        
        # 按钮
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        ttk.Button(button_frame, text="刷新", command=self.update_plot).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="重置", command=self.reset_view).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="帮助", command=self.show_help).pack(side=tk.LEFT)
        
        # 右侧内容区域
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 绘图区域
        plot_frame = ttk.LabelFrame(content_frame, text="三维投影图", padding="5")
        plot_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 创建matplotlib图形
        self.fig = Figure(figsize=(12, 8), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # 数据显示区域
        data_frame = ttk.LabelFrame(content_frame, text="测量数据与分析", padding="10")
        data_frame.pack(fill=tk.X)
        
        self.data_text = tk.Text(data_frame, height=12, font=("Courier", 10), wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(data_frame, orient=tk.VERTICAL, command=self.data_text.yview)
        self.data_text.configure(yscrollcommand=scrollbar.set)
        
        self.data_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_cube_vertices(self):
        """创建正方体顶点"""
        s = self.cube_size
        vertices = np.array([
            [0, 0, 0], [s, 0, 0], [s, s, 0], [0, s, 0],  # 底面 0,1,2,3
            [0, 0, s], [s, 0, s], [s, s, s], [0, s, s]   # 顶面 4,5,6,7
        ])
        return vertices
    
    def get_cube_faces(self):
        """获取正方体各面的顶点索引"""
        faces = {
            "底面": [0, 1, 2, 3],
            "顶面": [4, 5, 6, 7],
            "前面": [0, 1, 5, 4],
            "后面": [2, 3, 7, 6],
            "左面": [0, 3, 7, 4],
            "右面": [1, 2, 6, 5]
        }
        return faces
    
    def orthogonal_projection(self, point):
        """正投影: 垂直投影到xy平面"""
        return np.array([point[0], point[1], 0])
    
    def oblique_projection(self, point, angle_deg):
        """斜投影: 只在x方向产生变形 - 修正版算法"""
        angle_rad = math.radians(angle_deg)
        k = math.tan(angle_rad)
        # 关键修正: 只在x方向产生变形，y方向保持不变
        return np.array([point[0] + k * point[2], point[1], 0])
    
    def calculate_polygon_area(self, vertices):
        """使用shoelace公式计算多边形面积"""
        if len(vertices) < 3:
            return 0.0
        
        # 确保顶点按顺序排列
        vertices = np.array(vertices)
        n = len(vertices)
        area = 0.0
        
        for i in range(n):
            j = (i + 1) % n
            area += vertices[i][0] * vertices[j][1]
            area -= vertices[j][0] * vertices[i][1]
        
        return abs(area) / 2.0
    
    def calculate_single_face_area(self, vertices_proj, face_name):
        """计算单个面的投影面积 - 只计算光线直接照射的面"""
        faces = self.get_cube_faces()
        indices = faces[face_name]
        
        # 获取面的投影顶点
        face_vertices = [vertices_proj[i][:2] for i in indices]  # 只取x,y坐标
        area = self.calculate_polygon_area(face_vertices)
        
        return area
    
    def get_visible_face_for_projection(self, mode):
        """根据投影模式确定主要可见面"""
        if mode == "orthogonal":
            # 正投影：主要看底面投影
            return "底面"
        else:
            # 斜投影：主要看底面投影（因为它最能体现斜投影特性）
            return "底面"
    
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
            ax1.set_title("正投影", fontsize=14, fontweight='bold', color='red')
            ax2.set_title(f"斜投影 ({self.angle_var.get():.1f}°)", fontsize=14, fontweight='bold', color='green')
        else:
            # 单一模式
            ax = self.fig.add_subplot(111, projection='3d')
            self.draw_projection(ax, mode)
            if mode == "orthogonal":
                ax.set_title("正投影", fontsize=16, fontweight='bold', color='red')
            else:
                ax.set_title(f"斜投影 ({self.angle_var.get():.1f}°)", fontsize=16, fontweight='bold', color='green')
        
        self.fig.tight_layout()
        self.canvas.draw()
        self.update_measurement_data()
    
    def draw_projection(self, ax, mode):
        """绘制投影 - 重写版"""
        # 创建正方体
        vertices = self.create_cube_vertices()
        faces = self.get_cube_faces()
        
        # 绘制原始正方体
        cube_faces = []
        for face_name, indices in faces.items():
            face_vertices = [vertices[i] for i in indices]
            cube_faces.append(face_vertices)
        
        cube = Poly3DCollection(cube_faces, alpha=0.3, facecolor='lightblue', 
                               edgecolor='blue', linewidth=1.5)
        ax.add_collection3d(cube)
        
        # 绘制正方体顶点
        ax.scatter(vertices[:, 0], vertices[:, 1], vertices[:, 2], 
                  color='blue', s=60, alpha=0.8, label='原始顶点')
        
        # 绘制投影面(xy平面)
        s = self.cube_size
        margin = 2
        if mode == "oblique":
            # 斜投影需要更大的投影面
            angle = self.angle_var.get()
            extension = s * math.tan(math.radians(angle))
            xx, yy = np.meshgrid(np.linspace(-margin, s + extension + margin, 10), 
                                np.linspace(-margin, s + margin, 10))
        else:
            xx, yy = np.meshgrid(np.linspace(-margin, s + margin, 10), 
                                np.linspace(-margin, s + margin, 10))
        
        zz = np.zeros_like(xx)
        ax.plot_surface(xx, yy, zz, alpha=0.15, color='lightgray')
        
        # 计算投影点
        if mode == "orthogonal":
            vertices_proj = np.array([self.orthogonal_projection(v) for v in vertices])
            line_color = 'red'
            proj_color = 'lightcoral'
        else:
            angle = self.angle_var.get()
            vertices_proj = np.array([self.oblique_projection(v, angle) for v in vertices])
            line_color = 'green'
            proj_color = 'lightgreen'
        
        # 绘制投射线
        for i, (v, vp) in enumerate(zip(vertices, vertices_proj)):
            ax.plot([v[0], vp[0]], [v[1], vp[1]], [v[2], vp[2]], 
                   color=line_color, linewidth=1.5, alpha=0.6)
        
        # 绘制投影点
        ax.scatter(vertices_proj[:, 0], vertices_proj[:, 1], vertices_proj[:, 2], 
                  color=line_color, s=60, alpha=0.9, label='投影点')
        
        # 绘制投影面
        proj_faces = []
        face_colors = []
        
        for face_name, indices in faces.items():
            face_proj_vertices = [vertices_proj[i] for i in indices]
            proj_faces.append(face_proj_vertices)
            
            # 计算面积以确定是否可见
            face_vertices_2d = [vertices_proj[i][:2] for i in indices]
            area = self.calculate_polygon_area(face_vertices_2d)
            
            if area > 0.01:  # 可见面
                face_colors.append(proj_color)
            else:  # 不可见面
                face_colors.append('lightgray')
        
        proj_collection = Poly3DCollection(proj_faces, alpha=0.4, 
                                         facecolors=face_colors, 
                                         edgecolor=line_color, linewidth=2)
        ax.add_collection3d(proj_collection)
        
        # 设置坐标轴
        ax.set_xlabel('X (cm)', fontsize=10)
        ax.set_ylabel('Y (cm)', fontsize=10)
        ax.set_zlabel('Z (cm)', fontsize=10)
        
        # 设置视角
        ax.view_init(elev=self.elev_var.get(), azim=self.azim_var.get())
        
        # 设置坐标轴范围
        if mode == "oblique":
            max_angle = 60
            max_extension = s * math.tan(math.radians(max_angle))
            ax.set_xlim([-2, s + max_extension + 2])
        else:
            ax.set_xlim([-2, s + 2])
        
        ax.set_ylim([-2, s + 2])
        ax.set_zlim([-1, s + 2])
        
        # 设置纵横比
        ax.set_box_aspect([1, 1, 0.8])
        
        # 添加图例
        ax.legend(loc='upper right')
    
    def update_measurement_data(self):
        """更新测量数据 - 只计算单个面的投影面积"""
        self.data_text.delete(1.0, tk.END)
        
        vertices = self.create_cube_vertices()
        s = self.cube_size
        angle = self.angle_var.get()
        
        # 计算投影数据
        vertices_ortho = np.array([self.orthogonal_projection(v) for v in vertices])
        vertices_oblique = np.array([self.oblique_projection(v, angle) for v in vertices])
        
        # 只计算底面的投影面积（光线直接照射的面）
        ortho_area = self.calculate_single_face_area(vertices_ortho, "底面")
        oblique_area = self.calculate_single_face_area(vertices_oblique, "底面")
        
        # 理论计算
        cos_theta = math.cos(math.radians(angle)) if angle > 0 else 1.0
        theoretical_ratio = 1 / cos_theta
        
        # 生成报告
        report = self.generate_single_face_report(s, angle, ortho_area, oblique_area, theoretical_ratio)
        
        self.data_text.insert(1.0, report)
    
    def generate_analysis_report(self, cube_size, angle, ortho_areas, oblique_areas, theoretical_ratio):
        """生成完整的分析报告"""
        report = "=" * 60 + "\n"
        report += "正投影与斜投影对比实验 - 完整分析报告\n"
        report += "=" * 60 + "\n\n"
        
        # 基本信息
        report += "【实验参数】\n"
        report += f"正方体边长: {cube_size:.2f} cm\n"
        report += f"单个面面积: {cube_size*cube_size:.2f} cm²\n"
        report += f"斜投影角度: {angle:.1f}°\n"
        report += f"理论变形系数: {theoretical_ratio:.4f}\n\n"
        
        # 正投影数据
        report += "【正投影各面面积】\n"
        ortho_visible = 0
        ortho_total = 0
        for face_name, area in ortho_areas.items():
            if area > 0.01:
                ortho_visible += 1
                ortho_total += area
                report += f"{face_name:4s}: {area:8.2f} cm² ✓ 可见\n"
            else:
                report += f"{face_name:4s}: {area:8.2f} cm² ✗ 不可见\n"
        
        report += f"可见面数: {ortho_visible}\n"
        report += f"投影总面积: {ortho_total:.2f} cm²\n\n"
        
        # 斜投影数据
        report += f"【斜投影各面面积 (角度: {angle:.1f}°)】\n"
        oblique_visible = 0
        oblique_total = 0
        for face_name, area in oblique_areas.items():
            if area > 0.01:
                oblique_visible += 1
                oblique_total += area
                report += f"{face_name:4s}: {area:8.2f} cm² ✓ 可见\n"
            else:
                report += f"{face_name:4s}: {area:8.2f} cm² ✗ 不可见\n"
        
        report += f"可见面数: {oblique_visible}\n"
        report += f"投影总面积: {oblique_total:.2f} cm²\n\n"
        
        # 对比分析
        report += "【关键发现与分析】\n"
        
        # 可见面数对比
        if oblique_visible > ortho_visible:
            report += f"✓ 斜投影显示更多面: {oblique_visible} > {ortho_visible}\n"
        elif oblique_visible < ortho_visible:
            report += f"✗ 斜投影显示更少面: {oblique_visible} < {ortho_visible}\n"
        else:
            report += f"- 可见面数相同: {oblique_visible} = {ortho_visible}\n"
        
        # 总面积对比
        if oblique_total > ortho_total:
            increase = ((oblique_total / ortho_total) - 1) * 100
            report += f"✓ 斜投影总面积更大: {oblique_total:.2f} > {ortho_total:.2f}\n"
            report += f"  面积增加: {increase:.1f}%\n"
        elif oblique_total < ortho_total:
            decrease = ((ortho_total / oblique_total) - 1) * 100
            report += f"✗ 斜投影总面积更小: {oblique_total:.2f} < {ortho_total:.2f}\n"
            report += f"  面积减少: {decrease:.1f}%\n"
        else:
            report += f"- 投影总面积相同: {oblique_total:.2f} = {ortho_total:.2f}\n"
        
        # 特殊情况分析
        if angle == 0:
            report += "\n✓ 特殊情况: 角度为0°时，斜投影等同于正投影\n"
        else:
            # 分析各面的变化
            report += "\n【各面变化分析】\n"
            for face_name in ortho_areas.keys():
                ortho_area = ortho_areas[face_name]
                oblique_area = oblique_areas[face_name]
                
                if abs(ortho_area - oblique_area) < 0.01:
                    report += f"{face_name}: 面积不变 ({ortho_area:.2f} ≈ {oblique_area:.2f})\n"
                elif oblique_area > ortho_area + 0.01:
                    if ortho_area < 0.01:
                        report += f"{face_name}: 从不可见变为可见 (0 → {oblique_area:.2f})\n"
                    else:
                        change = ((oblique_area / ortho_area) - 1) * 100
                        report += f"{face_name}: 面积增加 {change:.1f}% ({ortho_area:.2f} → {oblique_area:.2f})\n"
                elif oblique_area < ortho_area - 0.01:
                    if oblique_area < 0.01:
                        report += f"{face_name}: 从可见变为不可见 ({ortho_area:.2f} → 0)\n"
                    else:
                        change = ((ortho_area / oblique_area) - 1) * 100
                        report += f"{face_name}: 面积减少 {change:.1f}% ({ortho_area:.2f} → {oblique_area:.2f})\n"
        
        # 理论验证
        actual_ratio = oblique_total / ortho_total if ortho_total > 0 else 1.0
        error = abs(theoretical_ratio - actual_ratio)
        
        report += f"\n【理论验证】\n"
        report += f"理论变形系数: {theoretical_ratio:.4f}\n"
        report += f"实际变形系数: {actual_ratio:.4f}\n"
        report += f"误差: {error:.4f}\n"
        
        if error < 0.1:
            report += "✓ 实验结果与理论高度吻合\n"
        elif error < 0.5:
            report += "△ 实验结果与理论基本吻合\n"
        else:
            report += "✗ 实验结果与理论存在较大差异\n"
        
        # 教育意义
        report += f"\n【教育意义】\n"
        report += "1. 斜投影的优势在于能显示更多信息，而非单纯的面积变化\n"
        report += "2. 平行于投影面的面在两种投影中面积相等\n"
        report += "3. 垂直于投影面的面在斜投影中变为可见\n"
        report += "4. 斜投影角度越大，变形效果越明显\n"
        report += "5. 理解投影原理有助于空间想象能力的培养\n"
        
        return report
    
    def generate_single_face_report(self, cube_size, angle, ortho_area, oblique_area, theoretical_ratio):
        """生成单个面投影面积的分析报告"""
        report = "=" * 50 + "\n"
        report += "单个面投影面积对比实验 - 分析报告\n"
        report += "=" * 50 + "\n\n"
        
        # 基本信息
        report += "【实验参数】\n"
        report += f"正方体边长: {cube_size:.2f} cm\n"
        report += f"底面原始面积: {cube_size*cube_size:.2f} cm²\n"
        report += f"斜投影角度: {angle:.1f}°\n"
        report += f"理论变形系数: {theoretical_ratio:.4f}\n\n"
        
        # 投影面积对比
        report += "【底面投影面积对比】\n"
        report += f"正投影面积: {ortho_area:.2f} cm²\n"
        report += f"斜投影面积: {oblique_area:.2f} cm²\n\n"
        
        # 面积变化分析
        if abs(ortho_area - oblique_area) < 0.01:
            report += "【关键发现】\n"
            report += f"✓ 面积保持不变: {ortho_area:.2f} ≈ {oblique_area:.2f} cm²\n"
            report += "✓ 这验证了理论：平行于投影面的面，投影面积不变\n\n"
        elif oblique_area > ortho_area:
            change = ((oblique_area / ortho_area) - 1) * 100
            report += "【关键发现】\n"
            report += f"✗ 面积增加: {change:.1f}% ({ortho_area:.2f} → {oblique_area:.2f})\n"
            report += "✗ 这与理论不符，可能存在计算错误\n\n"
        else:
            change = ((ortho_area / oblique_area) - 1) * 100
            report += "【关键发现】\n"
            report += f"✗ 面积减少: {change:.1f}% ({ortho_area:.2f} → {oblique_area:.2f})\n"
            report += "✗ 这与理论不符，可能存在计算错误\n\n"
        
        # 理论验证
        actual_ratio = oblique_area / ortho_area if ortho_area > 0 else 1.0
        error = abs(theoretical_ratio - actual_ratio)
        
        report += "【理论验证】\n"
        if angle == 0:
            report += "特殊情况：角度为0°时，斜投影等同于正投影\n"
            report += f"实际变形系数: {actual_ratio:.4f}\n"
            report += "✓ 符合理论预期\n\n"
        else:
            report += f"理论变形系数: {theoretical_ratio:.4f}\n"
            report += f"实际变形系数: {actual_ratio:.4f}\n"
            report += f"误差: {error:.4f}\n"
            
            if error < 0.01:
                report += "✓ 实验结果与理论高度吻合\n"
                report += "✓ 底面平行于投影面，面积应该保持不变\n\n"
            else:
                report += "✗ 实验结果与理论存在差异\n"
                report += "? 需要检查计算方法或投影算法\n\n"
        
        # 投影原理解释
        report += "【投影原理解释】\n"
        report += "对于底面（z=0的面）：\n"
        report += "• 正投影：P(x,y,0) → P'(x,y,0)\n"
        report += "• 斜投影：P(x,y,0) → P'(x+k·0, y, 0) = P'(x,y,0)\n"
        report += "• 结论：底面投影完全相同，面积应该相等\n\n"
        
        report += "用户的观察是正确的：\n"
        report += "• 斜投影只在x方向变形\n"
        report += "• 对于平行于投影面的面，面积应该保持不变\n"
        report += "• 这正是斜投影的重要特性\n\n"
        
        # 教育意义
        report += "【教育意义】\n"
        report += "1. 理解投影变换的本质：只有垂直分量产生变形\n"
        report += "2. 平行面不变性：平行于投影面的面积保持不变\n"
        report += "3. 斜投影的价值：显示更多信息，而非改变平行面面积\n"
        report += "4. 几何直觉的重要性：用户的质疑促进了理论理解\n"
        
        return report
    
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
        """重置视角和参数"""
        self.elev_var.set(20)
        self.azim_var.set(45)
        self.angle_var.set(30.0)
        self.angle_label.config(text="30.0°")
        self.update_plot()
    
    def show_help(self):
        """显示帮助信息"""
        help_text = """
正投影与斜投影对比实验程序 - 重写版

【程序特点】
✓ 修复了斜投影面积计算错误
✓ 完善了数据显示和分析功能
✓ 增加了详细的对比分析报告
✓ 提供了理论验证功能

【实验目的】
1. 理解正投影和斜投影的基本概念和区别
2. 观察不同投影方式下各面的可见性变化
3. 分析投影面积的变化规律和原因
4. 验证斜投影的理论公式

【重要发现】
• 斜投影的真正优势：能显示更多面，提供更完整的信息
• 平行面规律：平行于投影面的面，两种投影面积相等
• 垂直面规律：垂直于投影面的面，斜投影中变为可见
• 变形规律：角度越大，变形越明显

【使用说明】
1. 选择投影模式观察不同效果
2. 调节斜投影角度观察变化规律
3. 调节视角从不同方向观察
4. 查看详细的测量数据和分析报告

【投影原理】
• 正投影：P(x,y,z) → P'(x,y,0)
• 斜投影：P(x,y,z) → P'(x+k·z, y, 0)，其中k=tan(θ)

【版本信息】
版本: 2.0 (完全重写版)
基于修复总结报告重新编写
解决了所有已知问题
        """
        messagebox.showinfo("帮助", help_text)

def main():
    """主函数"""
    root = tk.Tk()
    app = ProjectionExperiment(root)
    root.mainloop()

if __name__ == "__main__":
    main()
