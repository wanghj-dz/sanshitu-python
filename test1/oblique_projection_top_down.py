#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
长方体从上往下斜投影程序
基于斜投影数学原理实现

作者：根据数学原理文档生成
日期：2025-11-01
"""

import numpy as np
import matplotlib.pyplot as plt
import math
from mpl_toolkits.mplot3d import Axes3D

class CuboidObliqueProjector:
    """
    长方体从上往下斜投影器
    实现斜投影的数学原理：x' = x - kx * z, y' = y - ky * z
    """
    
    def __init__(self, length=10, width=6, height=4):
        """
        初始化长方体参数
        
        Args:
            length: 长方体长度
            width: 长方体宽度  
            height: 长方体高度
        """
        self.length = length
        self.width = width
        self.height = height
        self.kx = 0.5  # x方向投影系数
        self.ky = 0.5  # y方向投影系数
        
    def set_projection_params(self, kx, ky):
        """
        设置投影参数
        
        Args:
            kx: x方向投影系数
            ky: y方向投影系数
        """
        self.kx = kx
        self.ky = ky
        
    def set_projection_angle(self, angle_deg=45, direction='isometric'):
        """
        设置投影角度
        
        Args:
            angle_deg: 投影角度（度）
            direction: 投影方向类型 ('isometric', 'dimetric', 'trimetric')
        """
        angle_rad = math.radians(angle_deg)
        
        if direction == 'isometric':
            # 斜等测投影：x和y方向偏移相同
            self.kx = math.tan(angle_rad) * math.cos(math.radians(45))
            self.ky = math.tan(angle_rad) * math.sin(math.radians(45))
        elif direction == 'dimetric':
            # 斜二测投影：只有x方向偏移
            self.kx = math.tan(angle_rad)
            self.ky = 0
        elif direction == 'trimetric':
            # 三测投影：自定义偏移比例
            self.kx = math.tan(angle_rad) * 0.75
            self.ky = math.tan(angle_rad) * 0.25
    
    def get_3d_vertices(self):
        """获取长方体的三维顶点"""
        vertices = np.array([
            [0, 0, 0],           # V0: 底面左下
            [self.length, 0, 0],  # V1: 底面右下
            [self.length, self.width, 0],  # V2: 底面右上
            [0, self.width, 0],  # V3: 底面左上
            [0, 0, self.height],  # V4: 顶面左下
            [self.length, 0, self.height],  # V5: 顶面右下
            [self.length, self.width, self.height],  # V6: 顶面右上
            [0, self.width, self.height]   # V7: 顶面左上
        ])
        return vertices
    
    def project_vertices(self, vertices_3d=None):
        """
        对顶点进行斜投影
        
        Args:
            vertices_3d: 可选的三维顶点数组
            
        Returns:
            投影后的二维顶点数组
        """
        if vertices_3d is None:
            vertices_3d = self.get_3d_vertices()
        
        vertices_2d = []
        for x, y, z in vertices_3d:
            # 斜投影公式：x' = x - kx * z, y' = y - ky * z
            x_proj = x - self.kx * z
            y_proj = y - self.ky * z
            vertices_2d.append((x_proj, y_proj))
        
        return np.array(vertices_2d)
    
    def build_projection_matrix(self):
        """构建斜投影矩阵"""
        proj_matrix = np.array([
            [1, 0, self.kx, 0],
            [0, 1, self.ky, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 1]
        ])
        return proj_matrix
    
    def project_with_matrix(self, vertices_3d=None):
        """使用矩阵进行投影"""
        if vertices_3d is None:
            vertices_3d = self.get_3d_vertices()
        
        proj_matrix = self.build_projection_matrix()
        
        # 添加齐次坐标
        homogeneous_vertices = np.hstack([
            vertices_3d, 
            np.ones((vertices_3d.shape[0], 1))
        ])
        
        # 应用矩阵变换
        projected_homogeneous = proj_matrix @ homogeneous_vertices.T
        
        # 转换回二维坐标
        projected_vertices = []
        for i in range(projected_homogeneous.shape[1]):
            x = projected_homogeneous[0, i] / projected_homogeneous[3, i]
            y = projected_homogeneous[1, i] / projected_homogeneous[3, i]
            projected_vertices.append((x, y))
        
        return np.array(projected_vertices)
    
    def draw_projection(self, show_3d=True, title="长方体从上往下斜投影"):
        """
        绘制投影图形
        
        Args:
            show_3d: 是否显示3D模型
            title: 图形标题
            
        Returns:
            投影后的二维顶点数组
        """
        vertices_2d = self.project_vertices()
        
        # 定义棱边连接关系
        edges = [
            # 底面棱边
            (0, 1), (1, 2), (2, 3), (3, 0),
            # 顶面棱边
            (4, 5), (5, 6), (6, 7), (7, 4),
            # 侧面棱边
            (0, 4), (1, 5), (2, 6), (3, 7)
        ]
        
        fig = plt.figure(figsize=(12, 8))
        
        if show_3d:
            # 显示3D模型
            ax1 = fig.add_subplot(121, projection='3d')
            vertices_3d = self.get_3d_vertices()
            
            # 绘制3D长方体
            for edge in edges:
                start, end = edge
                ax1.plot([vertices_3d[start, 0], vertices_3d[end, 0]],
                        [vertices_3d[start, 1], vertices_3d[end, 1]],
                        [vertices_3d[start, 2], vertices_3d[end, 2]], 'b-', linewidth=2)
            
            ax1.set_xlabel('X')
            ax1.set_ylabel('Y')
            ax1.set_zlabel('Z')
            ax1.set_title('长方体3D模型')
            ax1.grid(True)
            ax1.view_init(elev=30, azim=45)
            
            # 显示2D投影
            ax2 = fig.add_subplot(122)
        else:
            ax2 = fig.add_subplot(111)
        
        # 绘制2D投影
        for edge in edges:
            start, end = edge
            # 底面和侧面用实线，顶面用虚线
            if start < 4 or end < 4:
                ax2.plot([vertices_2d[start, 0], vertices_2d[end, 0]],
                        [vertices_2d[start, 1], vertices_2d[end, 1]], 
                        'b-', linewidth=2)
            else:
                ax2.plot([vertices_2d[start, 0], vertices_2d[end, 0]],
                        [vertices_2d[start, 1], vertices_2d[end, 1]], 
                        'r--', linewidth=2)
        
        # 标注顶点
        for i, (x, y) in enumerate(vertices_2d):
            ax2.text(x, y, f'V{i}', fontsize=10, ha='center', va='center',
                    bbox=dict(boxstyle='circle,pad=0.3', facecolor='yellow', alpha=0.5))
        
        ax2.set_xlabel('X投影坐标')
        ax2.set_ylabel('Y投影坐标')
        ax2.set_title(title)
        ax2.grid(True)
        ax2.axis('equal')
        
        plt.tight_layout()
        plt.show()
        
        return vertices_2d
    
    def calculate_dimensions(self):
        """计算投影后的尺寸"""
        vertices_2d = self.project_vertices()
        
        # 计算底面尺寸
        base_length = np.linalg.norm(vertices_2d[1] - vertices_2d[0])
        base_width = np.linalg.norm(vertices_2d[3] - vertices_2d[0])
        
        # 计算顶面尺寸
        top_length = np.linalg.norm(vertices_2d[5] - vertices_2d[4])
        top_width = np.linalg.norm(vertices_2d[7] - vertices_2d[4])
        
        # 计算高度投影
        height_proj = np.linalg.norm(vertices_2d[4] - vertices_2d[0])
        
        return {
            'base_length': base_length,
            'base_width': base_width,
            'top_length': top_length,
            'top_width': top_width,
            'height_projection': height_proj
        }

def demo_oblique_projection():
    """演示斜投影功能"""
    
    print("=== 长方体从上往下斜投影演示 ===")
    print("基于斜投影数学原理：x' = x - kx * z, y' = y - ky * z")
    print()
    
    # 创建投影器
    projector = CuboidObliqueProjector(length=10, width=6, height=4)
    
    # 1. 斜等测投影演示
    print("1. 斜等测投影演示")
    projector.set_projection_angle(angle_deg=45, direction='isometric')
    print(f"投影参数: kx={projector.kx:.4f}, ky={projector.ky:.4f}")
    
    vertices_2d = projector.draw_projection(show_3d=True, 
                                          title="长方体从上往下斜等测投影")
    dimensions = projector.calculate_dimensions()
    print("投影尺寸:", dimensions)
    print()
    
    # 2. 斜二测投影演示
    print("2. 斜二测投影演示")
    projector.set_projection_angle(angle_deg=26.56, direction='dimetric')
    print(f"投影参数: kx={projector.kx:.4f}, ky={projector.ky:.4f}")
    
    vertices_2d = projector.draw_projection(show_3d=True, 
                                          title="长方体从上往下斜二测投影")
    dimensions = projector.calculate_dimensions()
    print("投影尺寸:", dimensions)
    print()
    
    # 3. 自定义投影参数演示
    print("3. 自定义投影参数演示")
    projector.set_projection_params(kx=0.3, ky=0.7)
    print(f"投影参数: kx={projector.kx:.4f}, ky={projector.ky:.4f}")
    
    vertices_2d = projector.draw_projection(show_3d=True, 
                                          title="长方体从上往下自定义斜投影")
    dimensions = projector.calculate_dimensions()
    print("投影尺寸:", dimensions)
    print()
    
    # 4. 投影矩阵验证
    print("4. 投影矩阵验证")
    vertices_matrix = projector.project_with_matrix()
    vertices_direct = projector.project_vertices()
    
    # 比较两种方法的差异
    diff = np.max(np.abs(vertices_matrix - vertices_direct))
    print(f"矩阵投影与直接投影的最大差异: {diff:.6f}")
    print("两种方法结果一致" if diff < 1e-10 else "两种方法存在差异")

def interactive_demo():
    """交互式演示"""
    
    print("=== 交互式斜投影演示 ===")
    print("请输入长方体参数:")
    
    try:
        length = float(input("长度 (默认10): ") or 10)
        width = float(input("宽度 (默认6): ") or 6)
        height = float(input("高度 (默认4): ") or 4)
        
        projector = CuboidObliqueProjector(length, width, height)
        
        print("\n选择投影类型:")
        print("1. 斜等测投影 (45度)")
        print("2. 斜二测投影 (26.56度)")
        print("3. 自定义投影参数")
        
        choice = input("请选择 (1-3, 默认1): ") or "1"
        
        if choice == "1":
            projector.set_projection_angle(45, 'isometric')
            title = f"长方体斜等测投影 (L={length}, W={width}, H={height})"
        elif choice == "2":
            projector.set_projection_angle(26.56, 'dimetric')
            title = f"长方体斜二测投影 (L={length}, W={width}, H={height})"
        else:
            kx = float(input("x方向投影系数kx (默认0.5): ") or 0.5)
            ky = float(input("y方向投影系数ky (默认0.5): ") or 0.5)
            projector.set_projection_params(kx, ky)
            title = f"长方体自定义斜投影 (L={length}, W={width}, H={height})"
        
        print(f"\n投影参数: kx={projector.kx:.4f}, ky={projector.ky:.4f}")
        
        vertices_2d = projector.draw_projection(show_3d=True, title=title)
        dimensions = projector.calculate_dimensions()
        
        print("\n投影尺寸分析:")
        for key, value in dimensions.items():
            print(f"  {key}: {value:.2f}")
            
    except ValueError as e:
        print(f"输入错误: {e}")
    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    print("长方体从上往下斜投影程序")
    print("=" * 50)
    
    while True:
        print("\n选择演示模式:")
        print("1. 完整演示 (显示所有投影类型)")
        print("2. 交互式演示 (自定义参数)")
        print("3. 退出")
        
        choice = input("请选择 (1-3): ")
        
        if choice == "1":
            demo_oblique_projection()
        elif choice == "2":
            interactive_demo()
        elif choice == "3":
            print("程序结束")
            break
        else:
            print("无效选择，请重新输入")