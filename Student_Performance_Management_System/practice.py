import random

# 列表推导式，生成10个学生名字
names = [f'学生{i}' for  i in range(1,11)]
print("原始名单：", names)

# 列表推导式，生成10个随机成绩
scores = [random.randint(0,100) for _ in range(10)]
print("原始成绩：", scores)

# 使用字典推导式，将names与scores合并成一个字典
score_dict = {name: score for name, score in zip(names, scores)}
print("成绩字典：", score_dict)

# 新增学生
names.append('学生11')
score_dict.update({'学生11': 88})

# 筛选数据
excellent_students = [name for name, score in score_dict.items() if score >= 80]
print("优秀学生：", excellent_students)

# 修改数据
idx = names.index('学生5')
score_dict[names[idx]] = 100
print("修改后的成绩字典：", score_dict)

# 删除数据
score_dict.pop('学生3', None)
names.remove('学生3') # 同步更新列表

# 计算全班平均分（保留一位小数）
all_scores = list(score_dict.values())
avg_scores = round(sum(all_scores) / len(all_scores), 1)
max_student = max(score_dict, key=score_dict.get)
min_student = min(score_dict, key=score_dict.get)

print("平均分：", avg_scores)
print("最高分学生：", max_student)
print("最低分学生：", min_student)

# 排序
sorted_dict = {k: v for k, v in sorted(score_dict.items(), key=lambda item: item[1], reverse=True)}
print("排序后的字典：", sorted_dict)
