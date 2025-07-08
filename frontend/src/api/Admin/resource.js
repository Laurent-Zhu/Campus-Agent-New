import axios from 'axios';

export default {
    // 获取资源列表
    getResource(params) {
        return axios.get('/api/resources', { params });
    },
    // 上传资源
    uploadResource(data) {
        return axios.post('/api/resources', data, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        })
    }
}