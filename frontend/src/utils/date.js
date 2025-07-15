// src/utils/date.js
/**
 * 格式化日期为指定格式
 * @param {Date|string|number} date - 日期对象、时间戳或日期字符串
 * @param {string} format - 格式字符串（如 'YYYY-MM-DD HH:mm:ss'）
 * @returns {string} 格式化后的日期
 */
export function formatDate(date, format = 'YYYY-MM-DD HH:mm:ss') {
  if (!date) return '';
  // 处理日期对象
  const d = new Date(date);
  if (isNaN(d.getTime())) return ''; // 无效日期
  
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  const hours = String(d.getHours()).padStart(2, '0');
  const minutes = String(d.getMinutes()).padStart(2, '0');
  const seconds = String(d.getSeconds()).padStart(2, '0');
  
  // 替换格式字符串
  return format
    .replace('YYYY', year)
    .replace('MM', month)
    .replace('DD', day)
    .replace('HH', hours)
    .replace('mm', minutes)
    .replace('ss', seconds);
}