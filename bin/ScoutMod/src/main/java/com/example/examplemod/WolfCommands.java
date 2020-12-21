package com.example.examplemod;

import net.minecraft.entity.Entity;
import net.minecraft.entity.EntityLivingBase;
import net.minecraft.entity.EntityLiving;

import net.minecraft.entity.ai.EntityAIBase;
import net.minecraft.entity.ai.EntityAISit;
import net.minecraft.entity.ai.EntityAIFollowOwner;
import net.minecraft.entity.ai.EntityAITasks.EntityAITaskEntry;

import net.minecraft.entity.passive.EntityTameable;
import net.minecraft.entity.passive.EntityWolf; // (https://skmedix.github.io/ForgeJavaDocs/javadoc/forge/1.9.4-12.17.0.2051/net/minecraft/entity/passive/EntityWolf.html)
import net.minecraftforge.event.entity.EntityJoinWorldEvent;
import net.minecraftforge.fml.common.eventhandler.SubscribeEvent;
import net.minecraft.world.World; 
import net.minecraft.pathfinding.Path;
import net.minecraft.pathfinding.PathNavigate;
import net.minecraft.entity.player.EntityPlayer;
import net.minecraft.util.math.RayTraceResult;
import net.minecraft.util.math.BlockPos;
import net.minecraft.client.Minecraft;
import net.minecraft.client.multiplayer.WorldClient;

import java.util.*;


public class WolfCommands {

    public static EntityWolf getSpecificWolf(String name, World world) {
        System.out.format("[WOLFCOMMANDS] getSpecificWolf executing\n");
        EntityWolf wolf = null;
        List<Entity> entityList = world.getLoadedEntityList();
        for (Entity ent : entityList) {
            if (ent instanceof EntityWolf) {   
                System.out.format("\tExamining %s\n", ent.getName());
                System.out.format("\thasCustomName: %b, getCustomNameTag: %s\n", 
                                    ent.hasCustomName(), 
                                    ent.getCustomNameTag());
            }


            if (ent instanceof EntityWolf && 
                ent.hasCustomName() &&
                name.equals(ent.getCustomNameTag()) ) {
                System.out.format("[WOLFCOMMANDS] Found %s\n", ent.getCustomNameTag());
                wolf = (EntityWolf) ent;
                break;
            }
        }
        return wolf;
    }

    public static void removeAllTasks(EntityWolf wolf) {
        for (Object a : wolf.tasks.taskEntries.toArray()) {
                EntityAIBase task = ((EntityAITaskEntry) a).action;           
                System.out.format("[WOLFCOMMANDS] Removed task from wolf\n");
                wolf.tasks.removeTask(task);
            }
    }

    public static void followPlayer(EntityWolf wolf) {
        System.out.format("[WOLFCOMMANDS] followPlayer executing\n");
        // WolfCommands.removeAllTasks(wolf);
        // wolf.tasks.addTask(0, EntityAIFollowOwner(wolf, );
        
        // tryMoveToEntityLiving(Entity entityIn, double speedIn) 
        wolf.getAISit().setSitting(false);

        // enable follow user
        int priority = 6;
        EntityAIBase entryAction = new EntityAIFollowOwner((EntityTameable)wolf, 1.5F, 3.0F, 1000.0F);
        wolf.tasks.addTask(priority, entryAction);


        // wolf.getNavigation().a()
    }

    public static void sit(EntityWolf wolf) {
        System.out.format("[WOLFCOMMANDS] sit executing\n");
        wolf.getAISit().setSitting(true);
    }

    public static void goToWhereUserIsLooking(EntityWolf wolf) {
        System.out.format("[WOLFCOMMANDS] goToWhereUserIsLooking executing\n");
        RayTraceResult mop = Minecraft.getMinecraft().getRenderViewEntity().rayTrace(200, 1.0F);

        if (mop != null)
        {
            wolf.getAISit().setSitting(false);

            BlockPos blockPos = mop.getBlockPos(); 
            System.out.format("\tRaytrace hit Block at {%d %d %d}\n", blockPos.getX(), blockPos.getY(), blockPos.getZ());
            
            // disable follow user
            for (Object a : wolf.tasks.taskEntries.toArray()) {
                EntityAIBase entryAction = ((EntityAITaskEntry) a).action;
                
                if (entryAction instanceof EntityAIFollowOwner) {
                    wolf.tasks.removeTask(entryAction); // priority 6
                    // int priority = ((EntityAITaskEntry) a).priority;
                    // System.out.format("EntityAIFollowOwner Priority: %d\n", priority );
                }
            }
            
            // move to location
            PathNavigate nav = wolf.getNavigator();
            boolean result = nav.tryMoveToXYZ(blockPos.getX(), blockPos.getY(), blockPos.getZ(), 1.0F);
            System.out.format("\tWolf can move to location: {%b}\n", result);

        }
    }

    public static double distanceTo(BlockPos b1, BlockPos b2) {
        return Math.sqrt(Math.pow(b1.getX() - b2.getX(), 2) + Math.pow(b1.getY() - b2.getY(), 2) + Math.pow(b1.getZ() - b2.getZ(), 2));
    }

    public static void attackTarget(EntityWolf wolf, World world) {
        System.out.format("[WOLFCOMMANDS] attackTarget executing\n");
        RayTraceResult mop = Minecraft.getMinecraft().getRenderViewEntity().rayTrace(200, 1.0F);

        if (mop != null)
        {
            // get closest mob to block (within 10 blocks)
            List<Entity> entityList = world.getLoadedEntityList();
            Entity targetEntity = null;
            for (Entity ent : entityList) {
                if (!(ent instanceof EntityPlayer) && !(ent instanceof EntityWolf) && (ent instanceof EntityLiving)) {
                    BlockPos mopPos = mop.getBlockPos();
                    BlockPos targetPos = ent.getPosition();
                    double distance_from_block = WolfCommands.distanceTo(mopPos, targetPos);
                    System.out.format("\tDistance To %s: %f\n", ent.getName(), distance_from_block);
                    if (distance_from_block <= 10.0F) {
                        System.out.format("\tWolf found target\n");
                        targetEntity = ent;
                        break;
                    }
                } 
            }

            wolf.getAISit().setSitting(false);
            wolf.setAttackTarget((EntityLivingBase)targetEntity);
            

        }


    }
}