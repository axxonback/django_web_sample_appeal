from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
#from .tokens import UserActivateTokenGenerator


POST_MARK_LIKE = 1
POST_MARK_DISLIKE = 2
POST_MARKS = (
    (POST_MARK_LIKE, 'Like'),
    (POST_MARK_DISLIKE, 'Dislike')
)

class Post(models.Model):
    class Meta:
        ordering = ['-created']

    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, null=True, blank=True, related_name='posts')
    username = models.CharField(max_length=200, blank=True)
    body = models.TextField()
    tags = models.ManyToManyField('Tag')
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return self.body[:150]

    @property
    def comment_count(self):
        return self.comments.count()

    @property
    def liked_count(self):
        return self.marks.filter(mark_type=POST_MARK_LIKE).count()

    @property
    def disliked_count(self):
        return self.marks.filter(mark_type=POST_MARK_DISLIKE).count()

    def get_absolute_url(self):
        return '/post/{}'.format(self.id)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        PostHistory.objects.get_or_create(post=self)



class PostVersion(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey(Post)
    user = models.ForeignKey(User, null=True, blank=True, related_name='post_versions')
    username = models.CharField(max_length=200, blank=True)
    body = models.TextField()
    tags = models.ManyToManyField('Tag')
    email = models.EmailField(blank=True, null=True)


class PostHistory(models.Model):
    post = models.ForeignKey('Post', related_name='history')
    commented = models.DateTimeField(null=True, blank=True)
    up_voted = models.DateTimeField(null=True, blank=True)
    down_voted = models.DateTimeField(null=True, blank=True)
    un_voted = models.DateTimeField(null=True, blank=True)
    last_action = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        self.last_action = self.post.created
        if self.commented:
            self.last_action = max(self.last_action, self.commented)
        super().save(*args, **kwargs)


class PostMark(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey(Post, related_name='marks')
    mark_type = models.PositiveIntegerField(choices=POST_MARKS)
    user = models.ForeignKey(User, blank=True)

    def save(self, *args, **kwargs):
        type(self).objects.filter(post=self.post, user=self.user).delete()
        if self.user != self.post.user:
            super().save(*args, **kwargs)

        ph, created = PostHistory.objects.get_or_create(post=self.post)
        if self.mark_type == POST_MARK_LIKE:
            ph.up_voted = self.created
        else:
            ph.down_voted = self.created
        ph.save()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        ph, created = PostHistory.objects.get_or_create(post=self.post)
        ph.un_voted = timezone.now()
        ph.save()

class Tag(models.Model):
    class Meta:
        ordering = ('weight', 'title')

    title = models.CharField(max_length=500)
    alias = models.CharField(max_length=500)
    weight = models.IntegerField(default=0, blank=True)


class Comment(models.Model):
    class Meta:
        ordering = ['-created']

    created = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey(Post, related_name='comments')
    user = models.ForeignKey(User, null=True, blank=True, related_name='comments')
    username = models.CharField(max_length=200, blank=True)
    body = models.TextField()
    email = models.EmailField(blank=True, null=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        ph, created = PostHistory.objects.get_or_create(post=self.post)
        ph.commented = self.created
        ph.save()


    def get_absolute_url(self):
        return '/post/{}'.format(self.id)


    def __str__(self):
        return self.body[:150]

class CommentVersion(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    comment = models.ForeignKey(Comment)
    post = models.ForeignKey(Post, related_name='comment_versions')
    user = models.ForeignKey(User, null=True, blank=True, related_name='comment_versions')
    username = models.CharField(max_length=200, blank=True)
    body = models.TextField()
    email = models.EmailField(blank=True, null=True)


GOOGLE = 'google'
VK = 'vk'
FACEBOOK = 'facebook'

SOCIAL_NETWORKS = (
    (GOOGLE, 'google'),
    (VK, 'vk'),
    (FACEBOOK, 'facebook'),
)

class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='user_profile')
    receive_comments_email = models.BooleanField(default=True)
    email_confirmed = models.BooleanField(default=False)
    #activation_token = models.TextField(null=True, blank=True)

    #def save(self, *args, **kwargs):
    #    user = self.user
    #    token_generator = UserActivateTokenGenerator()
    #    token = token_generator.make_token(user)
    #    self.activation_token = token
    #    super().save(*args, **kwargs)

    def __str__(self):
        return self.user.username


class SocialAccount(models.Model):
    user = models.ForeignKey(User, related_name='social_accounts')
    external_id = models.CharField(max_length=500, null=True, blank=True)
    network = models.CharField(choices=SOCIAL_NETWORKS, max_length=20)


    def __str__(self):
        return "{} - {}".format(self.user.username, self.network)

def create_user_profile(sender, instance, created, **kwargs):
    profile, created = UserProfile.objects.get_or_create(user=instance)
    if created:
        profile.save()


post_save.connect(create_user_profile, sender=User)