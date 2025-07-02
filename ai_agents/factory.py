from .teacher.exam_generation.exam_generator import ExamGeneratorAgent

class AgentFactory:
    """智能体工厂类"""
    
    @staticmethod
    def create_agent(
        agent_type: str,
        **kwargs
    ):
        """
        创建智能体实例
        
        Args:
            agent_type: 智能体类型
            **kwargs: 其他参数
        
        Returns:
            BaseAgent: 智能体实例
        """
        # 根据类型创建对应的智能体
        if agent_type == "exam_generator":
            return ExamGeneratorAgent()
        else:
            return None