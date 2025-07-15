// 用于处理课件资源管理的 API 请求
import axios from 'axios'

const COURSEWARE_API_URL = "http://localhost:8001/api/django/administor/courseware/" // 暂时用这个

// 获取课件列表
export const fetchCoursewares = async (token) => {
    try {
        const response = await axios.get(COURSEWARE_API_URL, {
            headers: {
            'Authorization': `Bearer ${token}`
            }
    });
    return response.data;
    } catch (error) {
    console.error('获取课件列表失败:', error);
    throw error;
    }
};

// 删除课件
export const deleteCourseware = async (token, id) => {
    try {
        await axios.delete(COURSEWARE_API_URL + `${id}/`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        console.log('课件删除成功');
    } catch (error) {
        console.error('删除课件失败:', error);
        throw error;
    }
};

// 下载课件
export const downloadCourseware = async (token, coursewareId) => {
    try {
        const response = await axios.get(COURSEWARE_API_URL + `${coursewareId}/download/`, {
            headers: {
                'Authorization': `Bearer ${token}`
            },
            responseType: 'blob' // 以二进制形式接收响应数据
        });

        // 创建一个临时的 URL 对象
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        // 假设响应头中包含文件名信息
        const contentDisposition = response.headers['content-disposition'];
        const fileName = contentDisposition ? contentDisposition.split('filename=')[1].replace(/"/g, '') : 'courseware.pdf';
        link.setAttribute('download', fileName);
        document.body.appendChild(link);
        link.click();
        // 释放临时 URL 对象
        window.URL.revokeObjectURL(url);
        document.body.removeChild(link);
    } catch (error) {
        console.error('下载课件失败:', error);
        throw error;
    }
};